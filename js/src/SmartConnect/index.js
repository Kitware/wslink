/* global window */
import CompositeClosureHelper from '../CompositeClosureHelper';

import ProcessLauncher from '../ProcessLauncher';
import WebsocketConnection from '../WebsocketConnection';

export const DEFAULT_SESSION_MANAGER_URL = `${window.location.protocol}//${window.location.hostname}:${window.location.port}/paraview/`,
  DEFAULT_SESSION_URL = `${(window.location.protocol === 'https') ? 'wss' : 'ws'}://${window.location.hostname}:${window.location.port}/ws`;


function wsConnect(publicAPI, model) {
  const wsConnection = WebsocketConnection.newInstance({ urls: model.config.sessionURL, secret: model.config.secret, retry: model.config.retry });
  model.subscriptions.push(wsConnection.onConnectionReady(publicAPI.readyForwarder));
  model.subscriptions.push(wsConnection.onConnectionError(publicAPI.errorForwarder));
  model.subscriptions.push(wsConnection.onConnectionClose(publicAPI.closeForwarder));

  // Add to the garbage collector
  model.gc.push(wsConnection);

  return wsConnection.connect();
}

function smartConnect(publicAPI, model) {
  let session = null;
  model.gc = [];

  // Event forwarders
  publicAPI.readyForwarder = (data) => {
    session = data.getSession();
    publicAPI.fireConnectionReady(data);
  };
  publicAPI.errorForwarder = (data, err) => {
    publicAPI.fireConnectionError(data, err);
  };
  publicAPI.closeForwarder = (data) => {
    publicAPI.fireConnectionClose(data);
  };

  publicAPI.connect = () => {
    if (model.configDecorator) {
      model.config = model.configDecorator(model.config);
    }
    if (model.config.sessionURL) {
      // We have a direct connection URL
      session = wsConnect(publicAPI, model);
    } else {
      // We need to use the Launcher
      const launcher = ProcessLauncher.newInstance({ endPoint: model.config.sessionManagerURL || DEFAULT_SESSION_MANAGER_URL });

      model.subscriptions.push(launcher.onProcessReady((data) => {
        if (model.configDecorator) {
          model.config = model.configDecorator(Object.assign({}, model.config, data));
        } else {
          model.config = Object.assign({}, model.config, data);
        }

        session = wsConnect(publicAPI, model);
      }));
      model.subscriptions.push(launcher.onError((data) => {
        if (data && data.response && data.response.error) {
          publicAPI.errorForwarder(data, data.response.error);
        } else {
          // Try to use standard connection URL
          model.config.sessionURL = DEFAULT_SESSION_URL;
          session = wsConnect(publicAPI, model);
        }
      }));

      launcher.start(model.config);

      // Add to the garbage collector
      model.gc.push(launcher);
    }
  };

  publicAPI.getSession = () => {
    return session;
  };

  function cleanUp() {
    if (session) {
      session.close();
    }
    session = null;

    while (model.gc.length) {
      model.gc.pop().destroy();
    }
  }

  publicAPI.destroy = CompositeClosureHelper.chain(cleanUp, publicAPI.destroy);
}

const DEFAULT_VALUES = {
  config: {},
  // configDecorator: null,
};

export function extend(publicAPI, model, initialValues = {}) {
  Object.assign(model, DEFAULT_VALUES, initialValues);

  CompositeClosureHelper.destroy(publicAPI, model);
  CompositeClosureHelper.event(publicAPI, model, 'ConnectionReady');
  CompositeClosureHelper.event(publicAPI, model, 'ConnectionClose');
  CompositeClosureHelper.event(publicAPI, model, 'ConnectionError');
  CompositeClosureHelper.isA(publicAPI, model, 'SmartConnect');
  CompositeClosureHelper.get(publicAPI, model, ['config', 'configDecorator']);
  CompositeClosureHelper.set(publicAPI, model, ['configDecorator']);

  smartConnect(publicAPI, model);
}

// ----------------------------------------------------------------------------
export const newInstance = CompositeClosureHelper.newInstance(extend);

export default { newInstance, extend };
