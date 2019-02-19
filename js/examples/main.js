/* global document */
import WebsocketConnection from '../src/WebsocketConnection';
import SmartConnect from '../src/SmartConnect';

// this template allows us to use HtmlWebpackPlugin
// in webpack to generate our index.html
// expose-loader makes our 'export' functions part of the 'app' global
const htmlContent = `<button onClick="app.connect()">Connect</button>
<button onClick="app.wsclose()">Disconnect</button>
<br/>
<input type="text" value="1,2,3,4,5" class="input" />
<button onClick="app.sendInput('add')">Send Add</button>
<button onClick="app.sendInput('mult')">Send Mult</button>
<button onClick="app.sendBinary()">Send Binary</button>
<button onClick="app.toggleStream()">Sub/Unsub</button>
<button onClick="app.sendMistake()">Mistake</button>
<button onClick="app.postBinary()">send a float as binary</button>
<br/>
<textarea class="output" rows="12" cols="50"></textarea>
<br/>
<canvas class="imageCanvas" width="300px" height="300px"></canvas>
`;

const rootContainer = document.querySelector('body');
const controlContainer = document.createElement('div');
rootContainer.appendChild(controlContainer);
controlContainer.innerHTML = htmlContent;

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

export function sendInput(type) {
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

export function sendBinary() {
  if (!session) return;
  session.call('myprotocol.image', [])
    .then(handleMessage, (err) => logerr(err));
}

export function postBinary() {
  if (!session) return;
  session.call('myprotocol.postbinary', [
      session.addAttachment(new Float32Array([5678]).buffer),
  ]).then((r) => log('result ' + r), (err) => logerr(err));
}

export function sendMistake() {
  if (!session) return;
  session.call('myprotocol.mistake.TYPO', ['ignored'])
    .then(handleMessage, (err) => logerr(err));
}

export function toggleStream() {
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

export function wsclose() {
  if (!session) return;
  session.close();
  // it's fine to destroy the WebsocketConnection, but you won't get the WS close message.
  // if (ws) ws.destroy();
  // ws = null;
}

export function connect(direct=false) {
  ws = null;
  if (direct) {
    ws = WebsocketConnection.newInstance({ urls: 'ws://localhost:8080/ws' });
  } else {
    const config = { application: 'simple' };
    ws = SmartConnect.newInstance({ config });
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

// global.sendInput = sendInput;
// global.sendBinary = sendBinary;
// global.toggleStream = toggleStream;
// global.sendMistake = sendMistake;
// global.wsclose = wsclose;
// global.connect = connect;
