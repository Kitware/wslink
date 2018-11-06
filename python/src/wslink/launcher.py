import json
import logging
import io
import os
import re
import string
import subprocess
import sys
import time
import uuid

from random import choice

from twisted.internet import reactor, defer
from twisted.internet.task import deferLater
from twisted.internet.defer import CancelledError
from twisted.python import log
from twisted.web import server, resource, http
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.web.static import File

from wslink import upload

try:
    import argparse
except ImportError:
    from vtk.util import _argparse as argparse


sample_config_file = """
Here is a sample of what a configuration file could look like:

    {
        // ===============================
        // General launcher configuration
        // ===============================

        "configuration": {
            "host" : "localhost",
            "port" : 8080,
            "endpoint": "paraview",                   // SessionManager Endpoint
            "content": "/.../www",                    // Optional: Directory shared over HTTP
            "proxy_file" : "/.../proxy-mapping.txt",  // Proxy-Mapping file for Apache
            "sessionURL" : "ws://${host}:${port}/ws", // ws url used by the client to connect to the started process
            "timeout" : 25,                           // Wait time in second after process start
            "log_dir" : "/.../viz-logs",              // Directory for log files
            "upload_dir" : "/.../data",               // If launcher should act as upload server, where to put files
            "fields" : ["file", "host", "port", "updir"]     // List of fields that should be send back to client
                                                             // include "secret" if you provide it as an --authKey to the app
            "sanitize": {                             // Check information coming from the client
                "cmd": {
                    "type": "inList",                 // 'cmd' must be one of the strings in 'list'
                    "list": [
                        "me", "you", "something/else/altogether", "nothing-to-do"
                    ],
                    "default": "nothing-to-do"        // If the string doesn't match, replace it with the default.
                                                      // Include the default in your list
                },
                "cmd2": {                             // 'cmd2' must match the regexp provided, example: not a quote
                    "type": "regexp",
                    "regexp": "^[^\"]*$",             // Make sure to include '^' and '$' to match the entire string!
                    "default": "nothing"
                }
            }
        },

        // ===============================
        // Useful session vars for client
        // ===============================

        "sessionData" : { "updir": "/Home" },      // Tells client which path to updateFileBrowser after uploads

        // ===============================
        // Resources list for applications
        // ===============================

        "resources" : [ { "host" : "localhost", "port_range" : [9001, 9003] } ],

        // ===============================
        // Set of properties for cmd line
        // ===============================

        "properties" : {
            "vtkpython" : "/.../VTK/build/bin/vtkpython",
            "pvpython" : "/.../ParaView/build/bin/pvpython",
            "vtk_python_path": "/.../VTK/build/Wrapping/Python/vtk/web",
            "pv_python_path": "/.../ParaView/build/lib/site-packages/paraview/web",
            "plugins_path": "/.../ParaView/build/lib",
            "dataDir": "/.../path/to/data/directory"
        },

        // ===============================
        // Application list with cmd lines
        // ===============================

        "apps" : {
            "cone" : {
                "cmd" : [
                    "${vtkpython}", "${vtk_python_path}/vtk_web_cone.py", "--port", "$port" ],
                "ready_line" : "Starting factory"
            },
            "graph" : {
                "cmd" : [
                    "${vtkpython}", "${vtk_python_path}/vtk_web_graph.py", "--port", "$port",
                    "--vertices", "${numberOfVertices}", "--edges", "${numberOfEdges}" ],
                "ready_line" : "Starting factory"
            },
            "phylotree" : {
                "cmd" : [
                    "${vtkpython}", "${vtk_python_path}/vtk_web_phylogenetic_tree.py", "--port", "$port",
                    "--tree", "${dataDir}/visomics/${treeFile}", "--table", "${dataDir}/visomics/${tableFile}" ],
                "ready_line" : "Starting factory"
            },
            "filebrowser" : {
                "cmd" : [
                    "${vtkpython}", "${vtk_python_path}/vtk_web_filebrowser.py",
                    "--port", "${port}", "--data-dir", "${dataDir}" ],
                "ready_line" : "Starting factory"
            },
            "data_prober": {
                "cmd": [
                    "${pvpython}", "-dr", "${pv_python_path}/pv_web_data_prober.py",
                    "--port", "${port}", "--data-dir", "${dataDir}", "-f" ],
                "ready_line" : "Starting factory"
            },
            "visualizer": {
                "cmd": [
                    "${pvpython}", "-dr", "${pv_python_path}/pv_web_visualizer.py",
                    "--plugins", "${plugins_path}/libPointSprite_Plugin.so", "--port", "${port}",
                    "--data-dir", "${dataDir}", "--load-file", "${dataDir}/${fileToLoad}",
                    "--authKey", "${secret}", "-f" ],  // Use of ${secret} means it needs to be provided to the client, in "fields", above.
                "ready_line" : "Starting factory"
            },
            "loader": {
                "cmd": [
                    "${pvpython}", "-dr", "${pv_python_path}/pv_web_file_loader.py",
                    "--port", "${port}", "--data-dir", "${dataDir}",
                    "--load-file", "${dataDir}/${fileToLoad}", "-f" ],
                "ready_line" : "Starting factory"
            },
            "launcher" : {
                "cmd": [
                    "/.../ParaView/Web/Applications/Parallel/server/launcher.sh",
                    "${port}", "${client}", "${resources}", "${file}" ],
                "ready_line" : "Starting factory"
            },
            "your_app": {
                "cmd": [
                    "your_shell_script.sh", "--resource-host", "${host}", "--resource-port", "${port}",
                    "--session-id", "${id}", "--generated-password", "${secret}",
                    "--application-key", "${application}" ],
                "ready_line": "Output line from your shell script indicating process is ready"
        }
    }
"""

# =============================================================================
# Helper module methods
# =============================================================================

def remove_comments(json_like):
    """
    Removes C-style comments from *json_like* and returns the result.  Example::
        >>> test_json = '''\
        {
            "foo": "bar", // This is a single-line comment
            "baz": "blah" /* Multi-line
            Comment */
        }'''
        >>> remove_comments('{"foo":"bar","baz":"blah",}')
        '{\n    "foo":"bar",\n    "baz":"blah"\n}'

        From: https://gist.github.com/liftoff/ee7b81659673eca23cd9fc0d8b8e68b7
    """
    comments_re = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    def replacer(match):
        s = match.group(0)
        if s[0] == '/': return ""
        return s
    return comments_re.sub(replacer, json_like)

def generatePassword():
    return ''.join(choice(string.ascii_letters + string.digits) for _ in range(16))

# -----------------------------------------------------------------------------

def validateKeySet(obj, expected_keys, object_name):
    all_key_found = True
    for key in expected_keys:
        if not key in obj:
            print("ERROR: %s is missing %s key." % (object_name, key))
            all_key_found = False
    return all_key_found

def checkSanitize(key_pair, sanitize):
    if not sanitize:
     return
    for key in sanitize:
        if key in key_pair:
            checkItem = sanitize[key]
            value = key_pair[key]
            if checkItem["type"] == "inList":
                if not value in checkItem["list"]:
                    logging.warning("key %s: sanitize %s with default" % (key, key_pair[key]));
                    key_pair[key] = checkItem["default"]
            elif checkItem["type"] == "regexp":
                if not "compiled" in checkItem:
                    # User is responsible to add begin- and end- string symbols, to make sure entire string is matched.
                    checkItem["compiled"] = re.compile(checkItem["regexp"])
                if checkItem["compiled"].match(value) == None:
                    logging.warning("key %s: sanitize %s with default" % (key, key_pair[key]));
                    key_pair[key] = checkItem["default"]

# -----------------------------------------------------------------------------
# guard against malicious clients - make sure substitution is expected, if 'sanitize' is provided
def replaceVariables(template_str, variable_list, sanitize):
    for key_pair in variable_list:
        checkSanitize(key_pair, sanitize)
        item_template = string.Template(template_str)
        template_str = item_template.safe_substitute(key_pair)

    if "$" in template_str:
        logging.error("Some properties could not be resolved: " + template_str)

    return template_str

# -----------------------------------------------------------------------------

def replaceList(template_list, variable_list, sanitize):
    result_list = []
    for template_str in template_list:
        result_list.append(replaceVariables(template_str, variable_list, sanitize))
    return result_list

# -----------------------------------------------------------------------------

def filterResponse(obj, public_keys):
    public_keys.extend(['id', 'sessionURL', 'sessionManagerURL'])
    filtered_output = {}
    for field in obj:
        if field in public_keys:
            filtered_output[field] = obj[field]
    return filtered_output

# -----------------------------------------------------------------------------

def extractSessionId(request):
    path = request.path.split('/')
    if len(path) < 3:
       return None
    return str(path[2])

def jsonResponse(payload):
    return json.dumps(payload, ensure_ascii = False).encode('utf8')
# =============================================================================
# Session manager
# =============================================================================

class SessionManager(object):

    def __init__(self, config, mapping):
        self.sessions = {}
        self.config = config
        self.resources = ResourceManager(config["resources"])
        self.mapping = mapping
        self.sanitize = config["configuration"]["sanitize"]

    def createSession(self, options):
        # Assign id and store options
        id = str(uuid.uuid1())

        # Assign resource to session
        host, port = self.resources.getNextResource()

        # Do we have resources
        if host:
            options['id'] = id
            options['host'] = host
            options['port'] = port
            if not 'secret' in options:
                options['secret'] = generatePassword()
            options['sessionURL'] = replaceVariables(self.config['configuration']['sessionURL'], [options, self.config['properties']], self.sanitize)
            options['cmd'] = replaceList(self.config['apps'][options['application']]['cmd'], [options, self.config['properties']], self.sanitize)

            if 'sessionData' in self.config :
                for key in self.config['sessionData'] :
                    options[key] = replaceVariables(self.config['sessionData'][key], [options, self.config['properties']], self.sanitize)

            self.sessions[id] = options
            self.mapping.update(self.sessions)
            return options

        return None

    def deleteSession(self, id):
        host = self.sessions[id]['host']
        port = self.sessions[id]['port']
        self.resources.freeResource(host, port)
        del self.sessions[id]
        self.mapping.update(self.sessions)

    def getSession(self, id):
        if id in self.sessions:
            return self.sessions[id]
        return None

# =============================================================================
# Proxy manager
# =============================================================================

class ProxyMappingManager(object):

    def update(sessions):
        pass

class ProxyMappingManagerTXT(ProxyMappingManager):

    def __init__(self, file_path, pattern="%s %s:%d\n"):
        self.file_path = file_path
        self.pattern = pattern

    def update(self, sessions):
        with io.open(self.file_path, "w", encoding="utf-8") as map_file:
            for id in sessions:
                map_file.write(self.pattern % (id, sessions[id]['host'], sessions[id]['port']))

# =============================================================================
# Resource manager
# =============================================================================

class ResourceManager(object):
    """
    Class that provides methods to keep track on available resources (host/port)
    """
    def __init__(self, resourceList):
        self.resources = {}
        for resource in resourceList:
            host = resource['host']
            portList = list(range(resource['port_range'][0],resource['port_range'][1]+1))
            if host in self.resources:
                self.resources[host]['available'].extend(portList)
            else:
                self.resources[host] = { 'available': portList, 'used': []}

    def getNextResource(self):
        """
        Return a (host, port) pair if any available otherwise will return None
        """
        # find host with max availibility
        winner = None
        availibilityCount = 0
        for host in self.resources:
            if availibilityCount < len(self.resources[host]['available']):
                availibilityCount = len(self.resources[host]['available'])
                winner = host

        if winner:
            port = self.resources[winner]['available'].pop()
            self.resources[winner]['used'].append(port)
            return (winner, port)

        return (None, None)

    def freeResource(self, host, port):
        """
        Free a previously reserved resource
        """
        if host in self.resources and port in self.resources[host]['used']:
            self.resources[host]['used'].remove(port)
            self.resources[host]['available'].append(port)


# =============================================================================
# Process manager
# =============================================================================

class ProcessManager(object):
    def __init__(self, configuration):
        self.config = configuration
        self.log_dir = configuration['configuration']['log_dir']
        self.processes = {}

    def __del__(self):
        for id in self.processes:
            self.processes[id].terminate()

    def _getLogFilePath(self, id):
        return "%s%s%s.txt" % (self.log_dir, os.sep, id)

    def startProcess(self, session):
        proc = None

        # Create output log file
        logFilePath = self._getLogFilePath(session['id'])
        with io.open(logFilePath, mode="a+", buffering=1, encoding="utf-8") as log_file:
            try:
                proc = subprocess.Popen(session['cmd'], stdout=log_file, stderr=log_file)
                self.processes[session['id']] = proc
            except:
                logging.error("The command line failed")
                logging.error(' '.join(map(str, session['cmd'])))
                return None

        return proc

    def stopProcess(self, id):
        proc = self.processes[id]
        del self.processes[id]
        try:
            proc.terminate()
        except:
            pass # we tried

    def listEndedProcess(self):
        session_to_release = []
        for id in self.processes:
            if self.processes[id].poll() is not None:
                session_to_release.append(id)
        return session_to_release

    def isRunning(self, id):
        return self.processes[id].poll() is None

    # ========================================================================
    # Look for ready line in process output. Return True if found, False
    # otherwise. If no ready_line is configured and process is running return
    # False. This will then rely on the timout time.
    # ========================================================================

    def isReady(self, session, count = 0):
      id = session['id']

      # The process has to be running to be ready!
      if not self.isRunning(id) and count < 60:
        return False

      # Give up after 60 seconds if still not running
      if not self.isRunning(id):
        return True

      application = self.config['apps'][session['application']]
      ready_line  = application.get('ready_line', None)

      # If no ready_line is configured and the process is running then thats
      # enough.
      if not ready_line:
          return False

      ready = False

      # Check the output for ready_line
      logFilePath = self._getLogFilePath(session['id'])
      with io.open(logFilePath, "r", 1, encoding="utf-8") as log_file:
          for line in log_file.readlines():
              if ready_line in line:
                  ready = True
                  break

      return ready

# ===========================================================================
# Class to implement requests to POST, GET and DELETE methods
# ===========================================================================

class LauncherResource(resource.Resource, object):
    def __init__(self, options, config):
        super(LauncherResource, self).__init__()
        self._options = options
        self._config = config
        self.time_to_wait = int(config['configuration']['timeout'])
        self.field_filter = config['configuration']['fields']
        self.session_manager = SessionManager(config,ProxyMappingManagerTXT(config['configuration']['proxy_file']))
        self.process_manager = ProcessManager(config)


    def getChild(self, path, request):
        return self

    def __del__(self):
        try:
            # causes an exception when server is killed with Ctrl-C
            logging.warning("Server factory shutting down. Stopping all processes")
        except:
            pass

    # ========================================================================
    # Handle POST request
    # ========================================================================

    def render_POST(self, request):
        # Enable CORS
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'POST, GET, DELETE')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520) # 42 hours

        # import ipdb; ipdb.set_trace()
        payload = json.loads(request.content.getvalue())

        # Make sure the request has all the expected keys
        if not validateKeySet(payload, ["application"], "Launch request"):
            request.setResponseCode(http.BAD_REQUEST)
            return jsonResponse({"error": "The request is not complete"})

        # Try to free any available resource
        id_to_free = self.process_manager.listEndedProcess()
        for id in id_to_free:
            self.session_manager.deleteSession(id)
            self.process_manager.stopProcess(id)

        # Create new session
        session = self.session_manager.createSession(payload)

        # No resource available
        if not session:
            request.setResponseCode(http.SERVICE_UNAVAILABLE)
            return jsonResponse({"error": "All the resources are currently taken"})

        # Start process
        proc = self.process_manager.startProcess(session)

        if not proc:
            request.setResponseCode(http.SERVICE_UNAVAILABLE)
            return jsonResponse({"error": "The process did not properly start. %s" % str(session['cmd'])})

        # local function to act as errback for Deferred objects.
        def errback(error):
            # Filter out CancelledError and propagate rest
            if error.type != CancelledError:
                return error

        # Deferred object set to timeout request if process doesn't start in time
        timeout_deferred = deferLater(reactor, self.time_to_wait, lambda: request)
        timeout_deferred.addCallback(self._delayedRenderTimeout, session)
        timeout_deferred.addErrback(errback)
        # Make sure other deferred is canceled once one has been fired
        request.notifyFinish().addCallback(lambda x: timeout_deferred.cancel())

        # If a ready_line is configured create a Deferred object to wait for
        # ready line to be produced
        if 'ready_line' in self._config['apps'][session['application']]:
            ready_deferred = self._waitForReady(session, request)
            ready_deferred.addCallback(self._delayedRenderReady, session)
            ready_deferred.addErrback(errback)
            # Make sure other deferred is canceled once one has been fired
            request.notifyFinish().addCallback(lambda x: ready_deferred.cancel())

        return NOT_DONE_YET


    # ========================================================================
    # Wait for session to be ready. Rather than blocking keep using callLater(...)
    # to schedule self in reactor. Return a Deferred object whose callback will
    # be triggered when the session is ready
    # ========================================================================

    def _waitForReady(self, session, request, count=0, d=None):
        if not d:
            d = defer.Deferred()

        if not 'startTimedOut' in session and \
            not self.process_manager.isReady(session, count + 1):
            reactor.callLater(1, self._waitForReady, session, request, count + 1, d)
        else:
            d.callback(request)

        return d

    # ========================================================================
    # Called when the timeout out expires. Check if process is now ready
    # and send response to client.
    # ========================================================================

    def _delayedRenderTimeout(self, request, session):
        ready = self.process_manager.isReady(session, 0)

        if ready:
            request.write(jsonResponse(filterResponse(session, self.field_filter)))
            request.setResponseCode(http.OK)
        else:
            request.write(jsonResponse({"error": "Session did not start before timeout expired. Check session logs."}))
            # Mark the session as timed out and clean up the process
            session['startTimedOut'] = True
            self.session_manager.deleteSession(session['id'])
            self.process_manager.stopProcess(session['id'])
            request.setResponseCode(http.SERVICE_UNAVAILABLE)

        request.finish()

    # ========================================================================
    # Called when the process is ready ( the ready line has been read from the
    # process output).
    # ========================================================================

    def _delayedRenderReady(self, request, session):
        filterkeys = self.field_filter
        if session['secret'] in session['cmd']:
            filterkeys = self.field_filter + [ 'secret' ]
        request.write(jsonResponse(filterResponse(session, filterkeys)))
        request.setResponseCode(http.OK)

        request.finish()

    # =========================================================================
    # Handle GET request
    # =========================================================================

    def render_GET(self, request):
        # Enable CORS
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'POST, GET, DELETE')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520) # 42 hours

        id = extractSessionId(request)

        if not id:
           message = "id not provided in GET request"
           logging.error(message)
           request.setResponseCode(http.BAD_REQUEST)
           return jsonResponse({"error":message})

        logging.info("GET request received for id: %s" % id)

        session = self.session_manager.getSession(id)
        if not session:
           message = "No session with id: %s" % id
           logging.error(message)
           request.setResponseCode(http.NOT_FOUND)
           return jsonResponse({"error":message})

        # Return session meta-data
        request.setResponseCode(http.OK)
        return jsonResponse(filterResponse(session, self.field_filter))

    # =========================================================================
    # Handle DELETE request
    # =========================================================================

    def render_DELETE(self, request):
        # Enable CORS
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'POST, GET, DELETE')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', 2520) # 42 hours

        id = extractSessionId(request)

        if not id:
           message = "id not provided in DELETE request"
           logging.error(message)
           request.setResponseCode(http.BAD_REQUEST)
           return jsonResponse({"error":message})

        logging.info("DELETE request received for id: %s" % id)

        session = self.session_manager.getSession(id)
        if not session:
           message = "No session with id: %s" % id
           logging.error(message)
           request.setResponseCode(http.NOT_FOUND)
           return jsonResponse({"error":message})

        # Remove session
        self.session_manager.deleteSession(id)
        self.process_manager.stopProcess(id)

        message = "Deleted session with id: %s" % id
        logging.info(message)

        request.setResponseCode(http.OK)
        return session

# =============================================================================
# Start the web server
# =============================================================================

def startWebServer(options, config):
    # import pdb; pdb.set_trace()
    # Extract properties from config
    log_dir  = str(config["configuration"]["log_dir"])
    content  = str(config["configuration"]["content"])
    # twisted expects byte for uris.
    endpoint = str(config["configuration"]["endpoint"]).encode('utf-8')
    host     = str(config["configuration"]["host"])
    port     = int(config["configuration"]["port"])
    sanitize = config["configuration"]["sanitize"]

    # Setup logging
    logFileName = log_dir + os.sep + "launcherLog.log"
    formatting = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
    logging.basicConfig(level=logging.DEBUG, filename=logFileName, filemode='w', format=formatting)
    observer = log.PythonLoggingObserver()
    observer.start()
    if options.debug:
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(formatting)
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    # Initialize web resource
    web_resource = File(content) if (len(content) > 0) else resource.Resource()

    # Attach launcher
    web_resource.putChild(endpoint, LauncherResource(options, config))

    # Check if launcher should act as a file upload server as well
    if "upload_dir" in config["configuration"]:
        from upload import UploadPage
        updir = replaceVariables(config['configuration']['upload_dir'], [config['properties']], sanitize)
        uploadResource = UploadPage(updir)
        web_resource.putChild("upload", uploadResource)

    site = server.Site(web_resource)
    reactor.listenTCP(port, site, interface=host)
    reactor.run()

# =============================================================================
# Parse config file
# =============================================================================

def parseConfig(options):
    # Read values from the configuration file
    try:
        config_comments = remove_comments(io.open(options.config[0], encoding="utf-8").read())
        config = json.loads(config_comments)
    except:
        message = "ERROR: Unable to read config file.\n"
        message += str(sys.exc_info()[1]) + "\n" + str(sys.exc_info()[2])
        print(message)
        print(sample_config_file)
        sys.exit(2)

    expected_keys = ["configuration", "apps", "properties", "resources"]
    if not validateKeySet(config, expected_keys, "Config file"):
        print(sample_config_file)
        sys.exit(2)

    expected_keys = ["endpoint", "host", "port", "proxy_file", "sessionURL", "timeout", "log_dir", "fields"]
    if not validateKeySet(config["configuration"], expected_keys, "file.configuration"):
        print(sample_config_file)
        sys.exit(2)

    if not "content" in config["configuration"]:
        config["configuration"]["content"] = ""
    if not "sanitize" in config["configuration"]:
        config["configuration"]["sanitize"] = {}

    return config

# =============================================================================
# Setup default arguments to be parsed
#   -d, --debug
#   -t, --proxyFileType  Type of proxy file (txt, dbm)
# =============================================================================

def add_arguments(parser):
    parser.add_argument("config", type=str,  nargs=1,
        help="configuration file for the launcher")
    parser.add_argument("-d", "--debug",
        help="log debugging messages to stdout",
        action="store_true")

    return parser

# =============================================================================
# Parse arguments
# =============================================================================

def start(argv=None,
         description="wslink Web Launcher"):
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=sample_config_file)
    add_arguments(parser)
    args = parser.parse_args(argv)
    config = parseConfig(args)
    startWebServer(args, config)

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    start()
