#include "wsWebsocketConnection.h"

// use the wsWebsocketConnection class to invoke some methods
// on a ParaViewWeb server. Requires that the server run with
// a data directory that includes the standard ParaView data
// files
int main()
{
  wsLauncher launcher;
  launcher.DebugOn();
  json config;
  config["application"] = "pve";
  launcher.start("localhost", "8080", "/paraview", &config);

  wsWebsocketConnection ws(launcher.GetSecret());
  ws.DebugOn();
  ws.connect(launcher.GetServerHost(), launcher.GetServerPort(), launcher.GetServerTarget());

  json result;
  ws.send("file.server.directory.list", &result);

  json args =
  {
    {"relativePath", "disk_out_ref.ex2"}
  };
  ws.send("pv.proxy.manager.create.reader", &result, nullptr, &args);

  args =
  {
    "Contour", result["result"]["id"], json::object(), false
  };
  ws.send("pv.proxy.manager.create", &result, &args);
  std::string inputID = result["result"]["id"];

  args =
  {{
      {
        {"id", inputID},
        {"name", "SelectInputScalars"},
        {"value", { "POINTS", "Temp" } }
      }
  }};
  ws.send("pv.proxy.manager.update", &result, &args);

  args =
  {{
      {
        {"id", inputID},
        {"name", "ContourValues"},
        {"value", { 300.0, 500.0 } }
      }
  }};
  ws.send("pv.proxy.manager.update", &result, &args);

  ws.close();
}
