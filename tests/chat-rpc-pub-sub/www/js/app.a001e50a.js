(function(t){function e(e){for(var s,a,r=e[0],i=e[1],c=e[2],f=0,p=[];f<r.length;f++)a=r[f],Object.prototype.hasOwnProperty.call(o,a)&&o[a]&&p.push(o[a][0]),o[a]=0;for(s in i)Object.prototype.hasOwnProperty.call(i,s)&&(t[s]=i[s]);u&&u(e);while(p.length)p.shift()();return l.push.apply(l,c||[]),n()}function n(){for(var t,e=0;e<l.length;e++){for(var n=l[e],s=!0,r=1;r<n.length;r++){var i=n[r];0!==o[i]&&(s=!1)}s&&(l.splice(e--,1),t=a(a.s=n[0]))}return t}var s={},o={app:0},l=[];function a(e){if(s[e])return s[e].exports;var n=s[e]={i:e,l:!1,exports:{}};return t[e].call(n.exports,n,n.exports,a),n.l=!0,n.exports}a.m=t,a.c=s,a.d=function(t,e,n){a.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:n})},a.r=function(t){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},a.t=function(t,e){if(1&e&&(t=a(t)),8&e)return t;if(4&e&&"object"===typeof t&&t&&t.__esModule)return t;var n=Object.create(null);if(a.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var s in t)a.d(n,s,function(e){return t[e]}.bind(null,s));return n},a.n=function(t){var e=t&&t.__esModule?function(){return t["default"]}:function(){return t};return a.d(e,"a",e),e},a.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},a.p="";var r=window["webpackJsonp"]=window["webpackJsonp"]||[],i=r.push.bind(r);r.push=e,r=r.slice();for(var c=0;c<r.length;c++)e(r[c]);var u=i;l.push([0,"chunk-vendors"]),n()})({0:function(t,e,n){t.exports=n("56d7")},3145:function(t,e,n){"use strict";var s=n("adfa"),o=n.n(s);n.d(e,"default",(function(){return o.a}))},"56d7":function(t,e,n){"use strict";n.r(e);n("e260"),n("e6cf"),n("cca6"),n("a79d");var s=n("2b0e"),o=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",[t._v(" Welcome to WSLink demo application "),n("div",{class:t.$style.container},[n("div",{class:t.$style.line},[n("input",{directives:[{name:"model",rawName:"v-model",value:t.txt,expression:"txt"}],class:t.$style.input,domProps:{value:t.txt},on:{keyup:function(e){return!e.type.indexOf("key")&&t._k(e.keyCode,"enter",13,e.key,"Enter")?null:t.send.apply(null,arguments)},input:function(e){e.target.composing||(t.txt=e.target.value)}}}),n("button",{class:t.$style.button,on:{click:t.clear}},[t._v("Clear")])]),n("div",{class:t.$style.line},[n("button",{class:t.$style.button,on:{click:t.startTalking}},[t._v("Start")]),n("button",{class:t.$style.button,on:{click:t.stopTalking}},[t._v("Stop")])]),n("textarea",{class:t.$style.textarea,attrs:{disabled:"",rows:"20"},domProps:{value:t.allMessages}})])])},l=[],a=n("3835"),r=n("1bde"),i="wslink.communication.channel",c={name:"App",data:function(){return{allMessages:"",txt:"",session:null}},methods:{send:function(){this.session?(this.session.call("wslink.say.hello",[this.txt]),this.txt=""):this.allMessages+="Session is not available yet\n"},clear:function(){this.allMessages=""},startTalking:function(){this.session.call("wslink.start.talking")},stopTalking:function(){this.session.call("wslink.stop.talking")}},mounted:function(){var t=this;this.allMessages+="Try to connect to ws://".concat(window.location.host,"/ws\n");var e=r["a"].newInstance({urls:"ws://".concat(window.location.host,"/ws")});e.onConnectionClose((function(e){t.allMessages+="WS Close\n",t.allMessages+=JSON.stringify(e,null,2)})),e.onConnectionError((function(e){t.allMessages+="WS Error\n",t.allMessages+=JSON.stringify(e,null,2)})),e.onConnectionReady((function(){t.allMessages+="WS Connected\n",t.session=e.getSession(),t.session.subscribe(i,(function(e){var n=Object(a["a"])(e,1),s=n[0];t.allMessages+=s,t.allMessages+="\n"}))})),e.connect()}},u=c,f=n("3145"),p=n("2877");function d(t){this["$style"]=f["default"].locals||f["default"]}var y=Object(p["a"])(u,o,l,!1,d,null,null),v=y.exports;s["a"].config.productionTip=!1,new s["a"]({render:function(t){return t(v)}}).$mount("#app")},adfa:function(t,e,n){t.exports={container:"style_container_1KlI7",line:"style_line_3ZS9a",button:"style_button_oLJJW",input:"style_input_9RtjZ",textarea:"style_textarea_17TFe"}}});
//# sourceMappingURL=app.a001e50a.js.map