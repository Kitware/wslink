#include "../../../../cpp/wsWebsocketConnection.h"

#include <iostream>
#include <string>

const char* TOPIC  = "wslink.communication.channel";
const char* SECRET = "wslink-secret";
const char* HOST   = "127.0.0.1";
const char* PORT   = "8080";
const char* TARGET = "/ws";

using std::cout;
using std::endl;

int main(int argc, char *argv[])
{
  wsWebsocketConnection ws{SECRET};
  ws.connect(HOST, PORT, TARGET);

  ws.subscribe(TOPIC, 
      [](const json& json) -> void 
      {
        cout << json["id"] << " -> " << json["result"] << endl;
      });

  std::string line;
  while (std::cin >> line)
  {
    json args = { line.c_str() };
    ws.send("wslink.say.hello", nullptr, &args);
  }

  json result = {};
  ws.send("wslink.stop.talking", &result);

  return EXIT_SUCCESS;
}
