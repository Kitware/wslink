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
<button onClick="app.testNesting()">Test Nesting</button>
<button onClick="app.toggleStream()">Sub/Unsub</button>
<button onClick="app.sendMistake()">Mistake</button>
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
  console.log(msg);
  logOutput.innerHTML += msg;
  logOutput.innerHTML += '\n';
}
function logerr(err) {
  console.error(err);
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

export function testNesting() {
  if (!session) return;
  session.call('myprotocol.nested.image', [])
    .then((data) => {
      if (data['image']) handleMessage(data['image']);
      const onload = (e) => {
        const arr = new Uint8Array(e.target.result);
        if (arr.length === 4) {
          arr.forEach((d, i) => {
            if (d !== i + 1) console.error('mismatch4', d, i + 1);
          });
        } else if (arr.length === 6) {
          arr.forEach((d, i) => {
            if (d !== i + 5) console.error('mismatch6', d, i + 5);
          });
        } else {
          console.error('Size mismatch', arr.length);
        }
      };
      data.bytesList.forEach(bl => {
        const reader = new FileReader();
        reader.onload = onload;
        reader.readAsArrayBuffer(bl);
      });

      log('Open console to check for errors');
      console.log('Nesting:', data);
    }, (err) => logerr(err));
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
