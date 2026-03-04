import CompositeClosureHelper from "../CompositeClosureHelper";
// ----------------------------------------------------------------------------
// Dependency injection
// ----------------------------------------------------------------------------

let SMART_CONNECT_CLASS = null;

// ----------------------------------------------------------------------------

function setSmartConnectClass(klass) {
  SMART_CONNECT_CLASS = klass;
}

// ----------------------------------------------------------------------------
// Busy feedback handling
// ----------------------------------------------------------------------------

function busy(fn, update) {
  return (...args) =>
    new Promise((resolve, reject) => {
      update(1);
      fn(...args).then(
        (response) => {
          update(-1);
          resolve(response);
        },
        (error) => {
          update(-1);
          reject(error);
        }
      );
    });
}

// ----------------------------------------------------------------------------

function busyWrap(methodMap, update, skipList = []) {
  const busyContainer = {};
  Object.keys(methodMap).forEach((methodName) => {
    if (skipList.indexOf(methodName) === -1) {
      busyContainer[methodName] = busy(methodMap[methodName], update);
    } else {
      busyContainer[methodName] = methodMap[methodName];
    }
  });
  return busyContainer;
}

// ----------------------------------------------------------------------------
// vtkWSLinkClient
// ----------------------------------------------------------------------------

function vtkWSLinkClient(publicAPI, model) {
  // --------------------------------------------------------------------------
  // Internal methods
  // --------------------------------------------------------------------------

  function notifyBusy() {
    publicAPI.invokeBusyChange(model.busyCount);
  }

  // --------------------------------------------------------------------------

  function updateBusy(delta = 0) {
    model.busyCount += delta;

    // Clear any pending timeout
    if (model.timeoutId) {
      clearTimeout(model.timeoutId);
      model.timeoutId = 0;
    }

    // Delay notification when idle
    if (model.busyCount) {
      notifyBusy();
    } else {
      model.timeoutId = setTimeout(notifyBusy, model.notificationTimeout);
    }
  }

  // --------------------------------------------------------------------------
  // Public methods
  // --------------------------------------------------------------------------

  publicAPI.beginBusy = () => updateBusy(+1);
  publicAPI.endBusy = () => updateBusy(-1);
  publicAPI.isBusy = () => !!model.busyCount;
  publicAPI.isConnected = () => !!model.connection;

  // --------------------------------------------------------------------------

  publicAPI.connect = (config = {}, configDecorator = null) => {
    if (!SMART_CONNECT_CLASS) {
      return Promise.reject(new Error("Need to provide SmartConnect"));
    }
    if (model.connection) {
      return Promise.reject(new Error("Need to disconnect first"));
    }

    model.config = config;
    model.configDecorator = configDecorator || model.configDecorator;
    return new Promise((resolve, reject) => {
      model.smartConnect = SMART_CONNECT_CLASS.newInstance({
        config,
        configDecorator: model.configDecorator,
      });

      // ready
      model.smartConnect.onConnectionReady((connection) => {
        model.connection = connection;
        model.remote = {};
        model.config = model.smartConnect.getConfig();
        const session = connection.getSession();

        // Link remote API
        model.protocols = model.protocols || {};
        Object.keys(model.protocols).forEach((name) => {
          model.remote[name] = busyWrap(
            model.protocols[name](session),
            updateBusy,
            model.notBusyList
          );
        });

        // Forward ready info as well
        publicAPI.invokeConnectionReady(publicAPI);

        resolve(publicAPI);
      });

      // error
      model.smartConnect.onConnectionError((error) => {
        publicAPI.invokeConnectionError(error);
        reject(error);
      });

      // close
      model.smartConnect.onConnectionClose((close) => {
        publicAPI.invokeConnectionClose(close);
        reject(close);
      });

      // Start connection
      model.smartConnect.connect();
    });
  };

  // --------------------------------------------------------------------------

  publicAPI.disconnect = (timeout = 60) => {
    if (model.connection) {
      model.connection.destroy(timeout);
      model.connection = null;
    }
  };

  // --------------------------------------------------------------------------

  publicAPI.registerProtocol = (name, protocol) => {
    model.remote[name] = busyWrap(
      protocol(model.connection.getSession()),
      updateBusy,
      model.notBusyList
    );
  };

  // --------------------------------------------------------------------------

  publicAPI.unregisterProtocol = (name) => {
    delete model.remote[name];
  };
}

// ----------------------------------------------------------------------------
// Object factory
// ----------------------------------------------------------------------------

const DEFAULT_VALUES = {
  // protocols: null,
  // connection: null,
  // config: null,
  notBusyList: [],
  busyCount: 0,
  timeoutId: 0,
  notificationTimeout: 50,
  // configDecorator: null,
};

// ----------------------------------------------------------------------------

export function extend(publicAPI, model, initialValues = {}) {
  Object.assign(model, DEFAULT_VALUES, initialValues);

  // Object methods
  CompositeClosureHelper.set(publicAPI, model, [
    "protocols",
    "notBusyList",
    "configDecorator",
  ]);
  CompositeClosureHelper.get(publicAPI, model, [
    "connection",
    "config",
    "remote",
    "protocols",
    "notBusyList",
    "configDecorator",
  ]);
  CompositeClosureHelper.event(publicAPI, model, "BusyChange");
  CompositeClosureHelper.event(publicAPI, model, "ConnectionReady");
  CompositeClosureHelper.event(publicAPI, model, "ConnectionError");
  CompositeClosureHelper.event(publicAPI, model, "ConnectionClose");

  // Object specific methods
  vtkWSLinkClient(publicAPI, model);
}

// ----------------------------------------------------------------------------

export const newInstance = CompositeClosureHelper.newInstance(
  extend,
  "vtkWSLinkClient"
);

// ----------------------------------------------------------------------------

export default { newInstance, extend, setSmartConnectClass };
