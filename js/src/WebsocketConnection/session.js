// Helper borrowed from paraviewweb/src/Common/Core
import CompositeClosureHelper from '../CompositeClosureHelper';
import { UnChunker, generateChunks } from './chunking';
import { Encoder, Decoder } from '@msgpack/msgpack';

function defer() {
  const deferred = {};

  deferred.promise = new Promise(function (resolve, reject) {
    deferred.resolve = resolve;
    deferred.reject = reject;
  });

  return deferred;
}

function Session(publicAPI, model) {
  const CLIENT_ERROR = -32099;
  let msgCount = 0;
  const inFlightRpc = {};
  // matches 'rpc:client3:21'
  // client may be dot-separated and include '_'
  // number is message count - unique.
  // matches 'publish:dot.separated.topic:42'
  const regexRPC = /^(rpc|publish|system):(\w+(?:\.\w+)*):(?:\d+)$/;
  const subscriptions = {};
  let clientID = null;
  let MAX_MSG_SIZE = 512 * 1024;
  const unchunker = new UnChunker();

  // --------------------------------------------------------------------------
  // Private helpers
  // --------------------------------------------------------------------------

  function onCompleteMessage(payload) {
    if (!payload) return;
    if (!payload.id) return;
    if (payload.error) {
      const deferred = inFlightRpc[payload.id];
      if (deferred) {
        deferred.reject(payload.error);
      } else {
        console.error('Server error:', payload.error);
      }
    } else {
      const match = regexRPC.exec(payload.id);
      if (match) {
        const type = match[1];
        if (type === 'rpc') {
          const deferred = inFlightRpc[payload.id];
          if (!deferred) {
            console.log(
              'session message id without matching call, dropped',
              payload
            );
            return;
          }
          deferred.resolve(payload.result);
        } else if (type == 'publish') {
          console.assert(
            inFlightRpc[payload.id] === undefined,
            'publish message received matching in-flight rpc call'
          );
          // regex extracts the topic for us.
          const topic = match[2];
          if (!subscriptions[topic]) {
            return;
          }
          // for each callback, provide the message data. Wrap in an array, for back-compatibility with WAMP
          subscriptions[topic].forEach((callback) =>
            callback([payload.result])
          );
        } else if (type == 'system') {
          // console.log('DBG system:', payload.id, payload.result);
          const deferred = inFlightRpc[payload.id];
          if (payload.id === 'system:c0:0') {
            clientID = payload.result.clientID;
            MAX_MSG_SIZE = payload.result.maxMsgSize || MAX_MSG_SIZE;
            if (deferred) deferred.resolve(clientID);
          } else {
            console.error('Unknown system message', payload.id);
            if (deferred)
              deferred.reject({
                code: CLIENT_ERROR,
                message: `Unknown system message ${payload.id}`,
              });
          }
        } else {
          console.error('Unknown rpc id format', payload.id);
        }
      }
    }
    delete inFlightRpc[payload.id];
  }

  // --------------------------------------------------------------------------
  // Public API
  // --------------------------------------------------------------------------

  publicAPI.onconnect = (event) => {
    // send hello message
    const deferred = defer();
    const id = 'system:c0:0';
    inFlightRpc[id] = deferred;

    const wrapper = {
      wslink: '1.0',
      id,
      method: 'wslink.hello',
      args: [{ secret: model.secret }],
      kwargs: {},
    };

    const encoder = new CustomEncoder();
    const packedWrapper = encoder.encode(wrapper);

    for (let chunk of generateChunks(packedWrapper, MAX_MSG_SIZE)) {
      model.ws.send(chunk, { binary: true });
    }

    return deferred.promise;
  };

  // --------------------------------------------------------------------------

  publicAPI.call = (method, args = [], kwargs = {}) => {
    // create a promise that we will use to notify the caller of the result.
    const deferred = defer();
    // readyState OPEN === 1
    if (model.ws && clientID && model.ws.readyState === 1) {
      const id = `rpc:${clientID}:${msgCount++}`;
      inFlightRpc[id] = deferred;

      const wrapper = { wslink: '1.0', id, method, args, kwargs };

      const encoder = new CustomEncoder();
      const packedWrapper = encoder.encode(wrapper);

      for (let chunk of generateChunks(packedWrapper, MAX_MSG_SIZE)) {
        model.ws.send(chunk, { binary: true });
      }
    } else {
      deferred.reject({
        code: CLIENT_ERROR,
        message: `RPC call ${method} unsuccessful: connection not open`,
      });
    }
    return deferred.promise;
  };

  // --------------------------------------------------------------------------

  publicAPI.subscribe = (topic, callback) => {
    const deferred = defer();
    if (model.ws && clientID) {
      // we needs to track subscriptions, to trigger callback when publish is received.
      if (!subscriptions[topic]) subscriptions[topic] = [];
      subscriptions[topic].push(callback);
      // we can notify the server, but we don't need to, if the server always sends messages unconditionally.
      // model.ws.send(JSON.stringify({ wslink: '1.0', id: `subscribe:${msgCount++}`, method, args: [] }));
      deferred.resolve({ topic, callback });
    } else {
      deferred.reject({
        code: CLIENT_ERROR,
        message: `Subscribe call ${topic} unsuccessful: connection not open`,
      });
    }
    return {
      topic,
      callback,
      promise: deferred.promise,
      unsubscribe: () => publicAPI.unsubscribe({ topic, callback }),
    };
  };

  // --------------------------------------------------------------------------

  publicAPI.unsubscribe = (info) => {
    const deferred = defer();
    const { topic, callback } = info;
    if (!subscriptions[topic]) {
      deferred.reject({
        code: CLIENT_ERROR,
        message: `Unsubscribe call ${topic} unsuccessful: not subscribed`,
      });
      return deferred.promise;
    }
    const index = subscriptions[topic].indexOf(callback);
    if (index !== -1) {
      subscriptions[topic].splice(index, 1);
      deferred.resolve();
    } else {
      deferred.reject({
        code: CLIENT_ERROR,
        message: `Unsubscribe call ${topic} unsuccessful: callback not found`,
      });
    }
    return deferred.promise;
  };

  // --------------------------------------------------------------------------

  publicAPI.close = () => {
    const deferred = defer();
    // some transports might be able to close the session without closing the connection. Not true for websocket...
    model.ws.close();
    unchunker.releasePendingMessages();
    deferred.resolve();
    return deferred.promise;
  };

  // --------------------------------------------------------------------------

  function createDecoder() {
    return new Decoder();
  }

  publicAPI.onmessage = async (event) => {
    const message = await unchunker.processChunk(event.data, createDecoder);

    if (message) {
      onCompleteMessage(message);
    }
  };

  // --------------------------------------------------------------------------

  publicAPI.addAttachment = (payload) => {
    // Deprecated method, keeping it to avoid breaking compatibility
    // Now that we use msgpack to pack/unpack messages,
    // We can have binary data directly in the object itself,
    // without needing to transfer it separately from the rest.
    //
    // If an ArrayBuffer is passed, ensure it gets wrapped in
    // a DataView (which is what the encoder expects).
    if (payload instanceof ArrayBuffer) {
      return new DataView(payload);
    }

    return payload;
  };
}

const DEFAULT_VALUES = {
  secret: 'wslink-secret',
  ws: null,
};

export function extend(publicAPI, model, initialValues = {}) {
  Object.assign(model, DEFAULT_VALUES, initialValues);

  CompositeClosureHelper.destroy(publicAPI, model);
  CompositeClosureHelper.isA(publicAPI, model, 'Session');

  Session(publicAPI, model);
}

// ----------------------------------------------------------------------------

export const newInstance = CompositeClosureHelper.newInstance(extend);

// ----------------------------------------------------------------------------

export default { newInstance, extend };

class CustomEncoder extends Encoder {
  // Unfortunately @msgpack/msgpack only supports
  // views of an ArrayBuffer (DataView, Uint8Array,..),
  // but not an ArrayBuffer itself.
  // They suggest using custom type extensions to support it,
  // but that would yield a different packed payload
  // (1 byte larger, but most importantly it would require
  // dealing with the custom type when unpacking on the server).
  // Since this type is too trivial to be treated differently,
  // and since I don't want to rely on the users always wrapping
  // their ArrayBuffers in a view, I'm subclassing the encoder.
  encodeObject(object, depth) {
    if (object instanceof ArrayBuffer) {
      object = new DataView(object);
    }

    return super.encodeObject.call(this, object, depth);
  }
}
