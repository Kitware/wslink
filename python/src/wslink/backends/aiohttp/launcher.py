import argparse
import asyncio
import datetime
import io
import json
import logging
import os
import re
import string
import subprocess
import sys
import time
import uuid

from random import choice

import aiohttp.web as aiohttp_web

from . import _root_handler

from wslink.launcher import (
    SessionManager,
    ProxyMappingManagerTXT,
    ProcessManager,
    validateKeySet,
    STATUS_BAD_REQUEST,
    STATUS_SERVICE_UNAVAILABLE,
    filterResponse,
    STATUS_OK,
    extractSessionId,
    STATUS_NOT_FOUND,
)

# ===========================================================================
# Class to implement requests to POST, GET and DELETE methods
# ===========================================================================


class LauncherResource(object):
    def __init__(self, options, config):
        self._options = options
        self._config = config
        self.time_to_wait = int(config["configuration"]["timeout"])
        self.field_filter = config["configuration"]["fields"]
        self.session_manager = SessionManager(
            config, ProxyMappingManagerTXT(config["configuration"]["proxy_file"])
        )
        self.process_manager = ProcessManager(config)

    def __del__(self):
        try:
            # causes an exception when server is killed with Ctrl-C
            logging.warning("Server factory shutting down. Stopping all processes")
        except:
            pass

    # ========================================================================
    # Handle POST request
    # ========================================================================

    async def handle_post(self, request):
        payload = await request.json()

        # Make sure the request has all the expected keys
        if not validateKeySet(payload, ["application"], "Launch request"):
            return aiohttp_web.json_response(
                {"error": "The request is not complete"}, status=STATUS_BAD_REQUEST
            )

        # Try to free any available resource
        id_to_free = self.process_manager.listEndedProcess()
        for id in id_to_free:
            self.session_manager.deleteSession(id)
            self.process_manager.stopProcess(id)

        # Create new session
        session = self.session_manager.createSession(payload)

        # No resource available
        if not session:
            return aiohttp_web.json_response(
                {"error": "All the resources are currently taken"},
                status=STATUS_SERVICE_UNAVAILABLE,
            )

        # Start process
        proc = self.process_manager.startProcess(session)

        if not proc:
            err_msg = "The process did not properly start. %s" % str(session["cmd"])
            return aiohttp_web.json_response(
                {"error": err_msg}, status=STATUS_SERVICE_UNAVAILABLE
            )

        return await self._waitForReady(session, request)

    # ========================================================================
    # Wait for session to be ready
    # ========================================================================

    async def _waitForReady(self, session, request):
        start_time = datetime.datetime.now()
        check_line = "ready_line" in self._config["apps"][session["application"]]
        count = 0

        while True:
            if self.process_manager.isReady(session, count):
                filterkeys = self.field_filter
                if session["secret"] in session["cmd"]:
                    filterkeys = self.field_filter + ["secret"]
                return aiohttp_web.json_response(
                    filterResponse(session, filterkeys), status=STATUS_OK
                )

            elapsed_time = datetime.datetime.now() - start_time

            if elapsed_time.total_seconds() > self.time_to_wait:
                # Timeout is expired, if the process is not ready now, mark the
                # session as timed out, clean up the process, and return an error
                # response
                session["startTimedOut"] = True
                self.session_manager.deleteSession(session["id"])
                self.process_manager.stopProcess(session["id"])

                return aiohttp_web.json_response(
                    {
                        "error": "Session did not start before timeout expired. Check session logs."
                    },
                    status=STATUS_SERVICE_UNAVAILABLE,
                )

            await asyncio.sleep(1)
            count += 1

    # =========================================================================
    # Handle GET request
    # =========================================================================

    async def handle_get(self, request):
        id = extractSessionId(request)

        if not id:
            message = "id not provided in GET request"
            logging.error(message)
            return aiohttp_web.json_response(
                {"error": message}, status=STATUS_BAD_REQUEST
            )

        logging.info("GET request received for id: %s" % id)

        session = self.session_manager.getSession(id)
        if not session:
            message = "No session with id: %s" % id
            logging.error(message)
            return aiohttp_web.json_response(
                {"error": message}, status=STATUS_BAD_REQUEST
            )

        # Return session meta-data
        return aiohttp_web.json_response(
            filterResponse(session, self.field_filter), status=STATUS_OK
        )

    # =========================================================================
    # Handle DELETE request
    # =========================================================================

    async def handle_delete(self, request):
        id = extractSessionId(request)

        if not id:
            message = "id not provided in DELETE request"
            logging.error(message)
            return aiohttp_web.json_response(
                {"error": message}, status=STATUS_BAD_REQUEST
            )

        logging.info("DELETE request received for id: %s" % id)

        session = self.session_manager.getSession(id)
        if not session:
            message = "No session with id: %s" % id
            logging.error(message)
            return aiohttp_web.json_response(
                {"error": message}, status=STATUS_NOT_FOUND
            )

        # Remove session
        self.session_manager.deleteSession(id)
        self.process_manager.stopProcess(id)

        message = "Deleted session with id: %s" % id
        logging.info(message)

        return aiohttp_web.json_response(session, status=STATUS_OK)


# =============================================================================
# Start the web server
# =============================================================================


def startWebServer(options, config):
    # import pdb; pdb.set_trace()
    # Extract properties from config
    log_dir = str(config["configuration"]["log_dir"])
    content = str(config["configuration"]["content"])
    endpoint = str(config["configuration"]["endpoint"])
    host = str(config["configuration"]["host"])
    port = int(config["configuration"]["port"])
    sanitize = config["configuration"]["sanitize"]

    # Setup logging
    logFileName = log_dir + os.sep + "launcherLog.log"
    formatting = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=logging.DEBUG, filename=logFileName, filemode="w", format=formatting
    )
    if options.debug:
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(formatting)
        console.setFormatter(formatter)
        logging.getLogger("").addHandler(console)

    web_app = aiohttp_web.Application()

    launcher_resource = LauncherResource(options, config)

    if not endpoint.startswith("/"):
        endpoint = "/{0}/".format(endpoint)

    web_app.add_routes(
        [
            aiohttp_web.post(endpoint, launcher_resource.handle_post),
            aiohttp_web.get(endpoint, launcher_resource.handle_get),
            aiohttp_web.delete(endpoint, launcher_resource.handle_delete),
        ]
    )

    if len(content) > 0:
        web_app.router.add_route("GET", "/", _root_handler)
        web_app.add_routes([aiohttp_web.static("/", content)])

    aiohttp_web.run_app(web_app, host=host, port=port)
