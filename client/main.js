/* global document */
import WebsocketConnection from './WebsocketConnection';
import SmartConnect from './SmartConnect';

const inputElement = document.querySelector('.input');
const logOutput = document.querySelector('.output');
let ws = null;
let subscription = false;
let session = null;

function log(msg) {
  logOutput.innerHTML += msg;
  logOutput.innerHTML += '\n';
}
function logerr(err) {
  logOutput.innerHTML += `error: ${err.code}, "${err.message}", ${err.data}`;
  logOutput.innerHTML += '\n';
}

function sendInput(type) {
  if (!session) return;
  const data = JSON.parse('[' + inputElement.value + ']');
  session.call(`myprotocol.${type}`, [data])
    .then((result) => log('result ' + result), (err) => logerr(err));
}
function handleMessage(data) {
  let blob = Array.isArray(data) ? data[0].blob : data.blob;
  if (blob instanceof Blob) {
    const canvas = document.querySelector('.imageCanvas');
    const ctx = canvas.getContext('2d');

    const img = new Image();
    const reader = new FileReader();
    reader.onload = function(e) {
      img.onload = () => ctx.drawImage(img, 0, 0);
      img.src = e.target.result;
    };
    reader.readAsDataURL(blob);
  } else {
    log('result ' + blob);
  }
}

function sendBinary() {
  if (!session) return;
  session.call('myprotocol.image', [])
    .then(handleMessage, (err) => logerr(err));
}

function sendMistake() {
  if (!session) return;
  session.call('myprotocol.mistake.TYPO', ['ignored'])
    .then(handleMessage, (err) => logerr(err));
}

function toggleStream() {
  if (!subscription) {
    session.subscribe('image', handleMessage).then((result) => (subscription = result));
    session.call('myprotocol.stream', ['image'])
      .then((result) => log('result ' + result), (err) => logerr(err));
  } else {
    session.call('myprotocol.stop', ['image'])
      .then((result) => log('result ' + result), (err) => logerr(err));
    session.unsubscribe(subscription);
    subscription = null;
  }
}

function wsclose() {
  if (!session) return;
  session.close();
}

function connect(direct=false) {
  let ws = null;
  if (direct) {
    ws = WebsocketConnection.newInstance({ urls: 'ws://localhost:8080/ws' });
  } else {
    const config = { application: 'simple' };
    ws = new SmartConnect(config);
  }
  ws.onConnectionReady(() => {
    log('WS open');
    if (!session) {
      session = ws.getSession();
    }
    const canvas = document.querySelector('.imageCanvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, 300, 300);
  });

  ws.onConnectionClose(() => {
    log('WS close');
  });

  ws.onConnectionError((event) => {
    log('WS error');
    console.error(event);
  });

  session = ws.connect();
}

global.sendInput = sendInput;
global.sendBinary = sendBinary;
global.toggleStream = toggleStream;
global.sendMistake = sendMistake;
global.wsclose = wsclose;
global.connect = connect;
