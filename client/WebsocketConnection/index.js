import CompositeClosureHelper from '../../../../paraviewweb/src/Common/Core/CompositeClosureHelper';
import Session from './session';

function getTransportObject(url) {
  var idx = url.indexOf(':'),
    protocol = url.substring(0, idx);
  if (protocol === 'ws' || protocol === 'wss') {
    return {
      type: 'websocket',
      url,
    };
  }

  throw new Error(`Unknown protocol (${protocol}) for url (${url}).  Unable to create transport object.`);
}

function WebsocketConnection(publicAPI, model) {
  // TODO Should we try to reconnect on error?

  publicAPI.connect = () => {
    // without a URL we can't do anything.
    if (!model.urls) return null;
    // concat allows a single url or a list.
    var uriList = [].concat(model.urls),
      transports = [];

    for (let i = 0; i < uriList.length; i += 1) {
      const url = uriList[i];
      try {
        const transport = getTransportObject(url);
        transports.push(transport);
      } catch (transportCreateError) {
        console.error(transportCreateError);
      }
    }

    if (model.connection) {
      if (model.connection.url !== transports[0].url) {
        model.connection.close();
      } else if (model.connection.readyState === 0 || model.connection.readyState === 1) {
        // already connected.
        return model.session;
      }
    }

    model.connection = new WebSocket(transports[0].url);
    model.connection.binaryType = 'blob';
    model.session = Session.newInstance({ ws: model.connection, secret: model.secret });


    model.connection.onopen = (event) => {
      if (model.session) model.session.onconnect(event);

      publicAPI.fireConnectionReady();
    };

    model.connection.onclose = (event) => {
      publicAPI.fireConnectionClose();
      model.connection = null;
      // return !model.retry; // true => Stop retry
    };
    model.connection.onerror = (event) => {
      publicAPI.fireConnectionError(event);
    };
    // handle messages in the session.
    model.connection.onmessage = (event) => {
      model.session.onmessage(event);
    };
    return model.session;
  };

  publicAPI.getSession = () => (model.session);

  publicAPI.destroy = (timeout = 10) => {
    // publicAPI.off();
    if (model.session && timeout > 0) {
      // model.session.call('application.exit.later', [timeout]);
    }
    if (model.connection) {
      model.connection.close();
    }
    model.connection = null;
  };
}

const DEFAULT_VALUES = {
  secret: 'vtkweb-secret',
  connection: null,
  session: null,
  retry: false,
};

export function extend(publicAPI, model, initialValues = {}) {
  Object.assign(model, DEFAULT_VALUES, initialValues);

  CompositeClosureHelper.destroy(publicAPI, model);
  CompositeClosureHelper.event(publicAPI, model, 'ConnectionReady');
  CompositeClosureHelper.event(publicAPI, model, 'ConnectionClose');
  CompositeClosureHelper.event(publicAPI, model, 'ConnectionError');
  CompositeClosureHelper.isA(publicAPI, model, 'WebsocketConnection');

  WebsocketConnection(publicAPI, model);
}

// ----------------------------------------------------------------------------

export const newInstance = CompositeClosureHelper.newInstance(extend);

// ----------------------------------------------------------------------------

export default { newInstance, extend };
