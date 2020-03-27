import Vue from 'vue'
import App from 'wslink-pubsub/src/App'

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
