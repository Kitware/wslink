# wslink

Wslink allows easy, bi-directional communication between a python server and a
javascript or C++ client over a [websocket]. The client can make remote procedure
calls (RPC) to the server, and the server can publish messages to topics that
the client can subscribe to. The server can include binary attachments in
these messages, which are communicated as a binary websocket message, avoiding
the overhead of encoding and decoding.

## RPC and publish/subscribe

The initial users of wslink driving its development are [VTK] and [ParaView].
ParaViewWeb and vtkWeb require:
* RPC - a remote procedure call that can be fired by the client and return
  sometime later with a response from the server, possibly an error.

* Publish/subscribe - client can subscribe to a topic provided by the server,
  possibly with a filter on the parts of interest. When the topic has updated
  results, the server publishes them to the client, without further action on
  the client's part.

Wslink is replacing a communication layer based on Autobahn WAMP, and so one
of the goals is to be fairly compatible with WAMP, but simplify the interface
to the point-to-point communication we actually use.

## Examples

* Set up a Python (3.3+) [virtualenv] using requirements.txt. Roughly:
  - `cd wslink/python`
  - `pip install virtualenv`
  - `virtualenv runtime`
  - `source runtime/Scripts/activate` (on Windows)
  - `pip install -e .` (to use current wslink for development)
* Install node.js 10+ for the javascript client
* `cd wslink/js`
* `npm run test`
  - or:
* `npm run build:example`
* `cd ../tests/simple`
* `python server/simple.py`
  - starts a webserver at [localhost](http://localhost:8080/) with buttons to test RPC and pub/sub methods

## Existing API

Existing ParaViewWeb applications use these code patterns:
* @exportRPC decorator in Python server code to register a method as being remotely callable
* session.call("method.uri", [args]) in the JavaScript client to make an RPC call. Usually wrapped as an object method so it appears to be a normal class method.
* session.subscribe("method.uri", callback) in JS client to initiate a pub/sub relationship.
    * server calls self.publish("method.uri", result) to push info back to the client

We don't support introspection or initial handshake about which methods are
supported - the client and server must be in sync.

Message format:
```javascript
{
const request = {
    wslink: 1.0,
    id: `rpc:${clientId}:${count}`,
    method: 'myapp.render.window.image',
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
# add a binary attachment
def getImage(self):
    return {
        "size": [512, 512],
        "blob": session.addAttachment(memoryview(dataArray)),
        "mtime": dataArray.getMTime()
    }
```

### Binary attachments

session.addAttachment() takes binary data and stores it, returning a string key
that will be associated with the attachment. When a message is sent that uses
the attachment key, a text header message and a binary message is sent
beforehand with each attachment. The client will then substitute the binary
buffer for the string key when it receives the final message.

### Subscribe

The client tracks subscriptions - the server currently blindly sends out
messages for any data it produces which might be subscribed to. This is not
very efficient - if the client notifies the server of a subscription, it can
send the data only when someone is listening. The ParaViewWeb app Visualizer
makes an RPC call after subscribing to tell the server to start publishing.

### Handshake

When the client initially connects, it sends a 'hello' to authenticate with
the server, so the server knows this client can handle the messages it sends,
and the server can provide the client with a unique client ID - which the
client must embed in the rpc "id" field of its messages to the server.

* The first message the client sends should be hello, with the secret key provided by its launcher.
* Server authenticates the key, and responds with the client ID.
* If the client sends the wrong key or no key, the server responds with an authentication error message.

### Design

More extensive discussion in the [design](design.md) document.

[ParaView]: https://www.paraview.org/web/
[virtualenv]: https://virtualenv.pypa.io/
[VTK]: http://www.vtk.org/
[websocket]: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
