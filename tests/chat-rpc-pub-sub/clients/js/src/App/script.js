import WebsocketConnection from 'wslink/src/WebsocketConnection';

const TOPIC = 'wslink.communication.channel';

export default {
  name: 'App',
  data() {
    return {
      allMessages: '',
      txt: '',
      session: null,
    }
  },
  methods: {
    send() {
      if (this.session) {
        this.session.call('wslink.say.hello', [this.txt]);
        this.txt = '';
      } else {
        this.allMessages += 'Session is not available yet\n';
      }
    },
    clear() {
      this.allMessages = '';
    },
    startTalking() {
      this.session.call('wslink.start.talking');
    },
    stopTalking() {
      this.session.call('wslink.stop.talking');
    },
  },
  mounted() {
    this.allMessages += `Try to connect to ws://${window.location.host}/ws\n`;
    const ws = WebsocketConnection.newInstance({ urls: `ws://${window.location.host}/ws` });
    ws.onConnectionClose((event) => {
      this.allMessages += 'WS Close\n';
      this.allMessages += JSON.stringify(event, null, 2);
    });

    ws.onConnectionError((event) => {
      this.allMessages += 'WS Error\n';
      this.allMessages += JSON.stringify(event, null, 2);
    });

    ws.onConnectionReady(() => {
      this.allMessages += 'WS Connected\n';
      this.session = ws.getSession();

      this.session.subscribe(TOPIC, ([msg]) => {
        this.allMessages += msg;
        this.allMessages += '\n';
      });
    });

    ws.connect();
  },
}
