<template>
  <div>
    Welcome to WSLink demo application
    <div class="container">
      <div class="line">
        <input v-model="txt" v-on:keyup.enter="send" class="input" />
        <button @click="clear" class="button">Clear</button>
      </div>
      <div class="line">
        <button @click="startTalking" class="button">Start</button>
        <button @click="stopTalking" class="button">Stop</button>
      </div>
      <textarea :value="allMessages" disabled rows="20" class="textarea" />
    </div>
  </div>
</template>

<script>
import SmartConnect from "wslink/src/SmartConnect";

const TOPIC = "wslink.communication.channel";

export default {
  name: "App",
  data() {
    return {
      allMessages: "",
      txt: "",
      session: null,
    };
  },
  methods: {
    send() {
      if (this.session) {
        this.session.call("wslink.say.hello", [this.txt]);
        this.txt = "";
      } else {
        this.allMessages += "Session is not available yet\n";
      }
    },
    clear() {
      this.allMessages = "";
    },
    startTalking() {
      this.session.call("wslink.start.talking");
    },
    stopTalking() {
      this.session.call("wslink.stop.talking");
    },
  },
  mounted() {
    this.allMessages += `Try to connect\n`;
    const smartConnect = SmartConnect.newInstance({
      config: { application: "chat" },
    });

    smartConnect.onConnectionClose((event) => {
      this.allMessages += "WS Close\n";
      this.allMessages += JSON.stringify(event, null, 2);
    });

    smartConnect.onConnectionError((event) => {
      this.allMessages += "WS Error\n";
      this.allMessages += JSON.stringify(event, null, 2);
    });

    smartConnect.onConnectionReady((connection) => {
      this.allMessages += "WS Connected\n";
      this.session = connection.getSession();

      this.session.subscribe(TOPIC, ([msg]) => {
        console.log("receive msg from subscription");
        this.allMessages += msg;
        this.allMessages += "\n";
      });
    });

    smartConnect.connect();
  },
};
</script>

<style scoped>
.container {
  width: 400px;
}

.line {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
}

.button {
  width: 100px;
}

.input {
  flex: 1;
  margin-right: 10px;
}

.textarea {
  width: 390px;
  display: block;
  resize: none;
}
</style>
