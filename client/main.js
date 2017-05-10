/* global document */
import WebsocketConnection from './WebsocketConnection';

const inputElement = document.querySelector('.input');
const logOutput = document.querySelector('.output');
let ws = null;
let subscribed = false;
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
  if (data.blob instanceof Blob) {
    const canvas = document.querySelector('.imageCanvas');
    const ctx = canvas.getContext('2d');

    const img = new Image();
    const reader = new FileReader();
    reader.onload = function(e) {
      img.onload = () => ctx.drawImage(img, 0, 0);
      img.src = e.target.result;
    };
    reader.readAsDataURL(data.blob);
  } else {
    log('result ' + data.blob);
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
  if (!subscribed) {
    session.subscribe('image', handleMessage);
    session.call('myprotocol.stream', ['image'])
      .then((result) => log('result ' + result), (err) => logerr(err));
  } else {
    session.call('myprotocol.stop', ['image'])
      .then((result) => log('result ' + result), (err) => logerr(err));
    session.unsubscribe('image', handleMessage);
  }
  subscribed = !subscribed;
}

function wsclose() {
  if (!session) return;
  session.close();
}

function connect() {
  ws = WebsocketConnection.newInstance({ urls: 'ws://localhost:8080/ws' });

  ws.onConnectionReady(() => {
    log('WS open');
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
