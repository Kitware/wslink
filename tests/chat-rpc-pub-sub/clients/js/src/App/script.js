import SmartConnect from 'wslink/src/SmartConnect';

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
    this.allMessages += `Try to connect\n`;
    const smartConnect = SmartConnect.newInstance({ config: { application: 'chat'} });

    smartConnect.onConnectionClose((event) => {
      this.allMessages += 'WS Close\n';
      this.allMessages += JSON.stringify(event, null, 2);
    });

    smartConnect.onConnectionError((event) => {
      this.allMessages += 'WS Error\n';
      this.allMessages += JSON.stringify(event, null, 2);
    });

    smartConnect.onConnectionReady((connection) => {
      this.allMessages += 'WS Connected\n';
      this.session = connection.getSession();

      this.session.subscribe(TOPIC, ([msg]) => {
        console.log('receive msg from subscription')
        this.allMessages += msg;
        this.allMessages += '\n';
      });
    });

    smartConnect.connect();
  },
}
