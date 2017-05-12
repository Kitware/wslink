# wslink Design and Motivation
wslink grew out of several needs and pressures, and I've collected information
and notes about the background and design here.

## ParaViewWeb RPC and publish/subscribe

ParaViewWeb uses autobahn WAMP protocol for RPC and publish/subscribe messages
as of May 2017. Due to changes to autobahn's WAMP implementation, we can't
upgrade autobahn and continue using WAMP. We require:
* RPC - a remote procedure call that can be fired by the client and return sometime later with a response from the server, possibly an error.
* Publish/subscribe - client can subscribe to a topic provided by the server, possibly with a filter on the parts of interest. When the topic has updated results, the server publishes them to the client, without further action on the client's part.

We would also like:
* Real binary messages - WebSockets support binary messages, and one of our
major use cases is publishing images (rendered frames). WAMP only supports base64-encoded binary objects.
* Other webservers - WAMP has been implemented elsewhere, but in JavaScript
the only implementations require autobahn's router, crossbar.io. It would
be great to support Tornado and CherryPy as alternative webservers to Twisted/autobahn.

## Foundation

[jsonrpc](http://www.jsonrpc.org/specification) has a well-defined, simple, and easily implemented specification for using JSON to do RPC. It is transport agnostic, and language independent, so we can use it between javascript and python. There are many implementations, but we are free to use them or ignore them. JSON can represent four primitive types (Strings, Numbers, Booleans, and Null) and two structured types (Objects and Arrays). We want to extend our messages to handle binary objects, inserted into JSON dict/object, discussed below.

Websockets allow bi-directional communication between the server and client. Authentication needs to be addressed. 

Because we wish to support pub/sub, we make the client and server more symmetric than in the jsonrpc spec - the server can publish to the client after a subscription is made, so in jsonrpc terms, the server is making an RPC call to the client. So our server and client must both be able to make and receive jsonrpc calls.

Small examples have proven websocket and binary message support in twisted, tornado, and cherrypy, so if we can abstract the webserver sufficiently, we may be able to support all of these.

## Existing API

Existing ParaViewWeb applications use these code patterns:
* @exportRPC decorator in Python server code to register a method as being remotely callable
* session.call("method.uri", [args]) in the JavaScript client to make an RPC call. Usually wrapped as an object method so it appears to be a normal class method.
* session.subscribe("method.uri", callback) in JS client to initiate a pub/sub relationship.
    * server calls self.publish("method.uri", result) to push info back to the client

We don't support introspection or initial handshake about which methods are supported - the client and server must be in sync. Could the server supply the client with a list of RPC methods it supplies? Yes, but then the client couldn't operate unless it's connected to a server - it would call undefined methods, rather than calling those methods and getting a 'not connected' error. Maybe not a concern.

The 'session' object is provided by Autobahn|JS WAMP, so we need to replace it. 

## Jsonrpc implementations
An old [wiki page](https://en.wikipedia.org/w/index.php?title=JSON-RPC&oldid=731445841#Implementations) lists implementations - most are transport/server specific.

For Python, [Tinyrpc](https://tinyrpc.readthedocs.io/en/latest/) has a parser for messages that will do validity checking - seems useful. 

For Javascript, [jrpc](https://github.com/vphantom/js-jrpc) extends jsonrpc to be bi-directional, and includes a handshake to upgrade from standard jsonrpc. [RaptorRPC](https://github.com/LinusU/raptor-rpc) might be interesting.

Message format:
```javascript
{
const request = {
    wslink: 1.0,
    id: `rpc:${clientId}:${count}`,
    method: 'render.window.image',
    args: [],
    kwargs: { w: 512, h: 512 }
};

const response = {
    wslink: 1.0,
    id: `rpc:${clientId}:${count}`,
    result: {}, // either result or error, not both
    error: {}
};

// types used as prefix for id.
const types = ['rpc', 'publish', 'system']; 
}
```

```python
// add a binary attachment
def getImage(self):
    return {
        "size": [512, 512],
        "blob": session.addAttachment(memoryview(dataArray)),
        "mtime": dataArray.getMTime()
    }
```

## wslink.js
We would like to support kwargs, like wamp, which violates pure jsonrpc.
We can extend it by simply adding a 'kwargs' param, as above. Therefore we'll
use 'wslink' as our version string, instead of 'jsonrpc'. We also change from 'params' to 'args'.

AutobahnJS `session.call()` returns a Promise, except that IE doesn't support
promises, so it uses an alternative if needed. node_modules/autobahn/lib/session.js uses `self._defer()` to retrieve it. connection.js has the factory. 
ParaViewWeb uses babel-polyfill, which includes a Promise implementation.

We can use the same defer() pattern, where we store the resolve, reject
functions so we can call them when the message response is received.

### Binary attachments
session.addAttachment() takes binary data and stores it, returning a string
key that will be associated with the attachment. When a message is sent that
uses the attachment key, a binary message is sent beforehand with the
attachment. The client can then substitute the binary buffer for the string
key when it receives the final message. 

Now sending a text header message for each binary message to associate it with
a key.

### Subscribe
The client needs to know about subscriptions - the server can blindly send out
messages for any data it produces which might be subscribed to. This is not
very efficient - if the client notifies the server of a subscription, it can
send the data only when someone is listening.

### Handshake
When the client initially connects, it can authenticate with the server, so the
server knows this client can handle the messages it sends, and the server can
provide the client with a unique client ID - which the client can embed in the 
rpc "id" field of it's messages to the server.

* The first message client sends should be hello, with the secret key provided by it's launcher.
* Server authenicates the key, responds with the client ID.
* If the client doesn't send a key, the server can choose to serve an un-authenticated client, or respond with an authentication error message.

