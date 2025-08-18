# ProcessLauncher

The ProcessLauncher can be used to start remote python servers, or other
remote processes.
The ProcessLauncher is used in ParaViewWeb to start a new remote 
server instance to perform interactive 3D post-processing using either
a VTK or a ParaView backend.

```javascript
import ProcessLauncher from 'wslink/src/ProcessLauncher';

processLauncher = ProcessLauncher.newInstance({ endPoint: '/paraview' });

// Optionally you can provide a launcherRetry: [1000, 2000, 3000, 5000]
// with the set of time to wait in ms before another retry.
// Retries will only occured on a 503 response from the server.
```

## ProcessLauncher.newInstance({ endPoint, launcherRetry: [] })

Create a process launcher that will make requests to a remote
server using the provided endpoint url.

## start(config) 

Submit a request for a new remote process.

The config object gets posted via a POST request to the endpoint provided
at creation time.

The current ParaViewWeb server-side **Launcher** expects at least
the following object.

```js
{
    application: 'NameOfTheProcess',
}
```

But additional key/value pairs can be added depending on the needs of the targeted process.

Once the remote process becomes ready a notification is sent.

## fetchConnection(sessionId)

Trigger a request for getting the full connection information
based on an existing sessionId.

## stop(connection) 

Trigger a request to terminate a remote process using the connection
object that was provided at start time.

## listConnections()

Return the list of already established connections. (From that instance)

## onProcessReady(callback) : subscription

Register a callback for when a remote process becomes available after a start() request.

The callback function will then receive a json object describing how to connect to that remote process.

```js
{
    sessionURL: 'ws://myServer/proxy?sessionId=asdfwefasdfwerfqerfse',
    maybe: 'something else too'
}
```
## onProcessStopped(callback) : subscription

Register a callback for when a stop request is performed.

## onFetch(callback) : subscription

Register a callback for when a fetchConnection request is performed.

## onError(callback) : subscription

Register a callback for when an error occured regardless of the request.

## destroy()

Free memory and detatch any listeners.
