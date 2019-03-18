# wslink C++

Wslink allows easy, bi-directional communication between a python server and a
C++/C client over a [websocket]. The client can make RPC calls to the
server. Currently the C++ API supports websocket communications to an existing
server as well as the ability to launch servers.

The low level API is provided through the wsWebSocketConnection header file. There is also a hgiher level C++ API provided through the wsSimpleCient class.

## Example Client using the low level API

With error checking removed for brevity. See wstest.cxx for the full code.

```C++
int main()
{
  wsLauncher launcher;
  json config;
  config["application"] = "pve";
  launcher.start("localhost", "8080", "/paraview", &config);

  wsWebsocketConnection ws(launcher.GetSecret());
  ws.connect(launcher.GetServerHost(), launcher.GetServerPort(), launcher.GetServerTarget());

  // load a file
  json args =
  {
    {"relativePath", "disk_out_ref.ex2"}
  };
  ws.send("pv.proxy.manager.create.reader", &result, nullptr, &args);

  // Create a contour filter
  args =
  {
    "Contour", result["result"]["id"], json::object(), false
  };
  ws.send("pv.proxy.manager.create", &result, &args);
  std::string inputID = result["result"]["id"];

  // set the scalars to operate on
  args =
  {{
      {
        {"id", inputID},
        {"name", "SelectInputScalars"},
        {"value", { "POINTS", "Temp" } }
      }
  }};
  ws.send("pv.proxy.manager.update", &result, &args);

  // set the contour values
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
```

## Example Client using the high level API (untested)
```C++
int main()
{
  wsSimpleClient cl;
  cl.Initialize("localhost", "8080", "/paraview");

  int input = 0;
  cl.LoadDataSet("disk_out_ref.ex2", input);

  int iso = 0;
  std::vector<double> values;
  values.push(300.0);
  values.push(500.0);
  cl.IsoSurface(input,"Temp", values, iso);

  std::string scene;
  cl.GetDataAsGLTF(scene);

  ...

  cl.DeleteDataSet(iso);
  cl.DeleteDataSet(input);
}
```

## Get the whole story

This package is just the client side of wslink. See the [github repo] for
the full story - and to contribute or report issues!

## License
Free to use in open-source and commercial projects, under the BSD-3-Clause license.

[github repo]: https://github.com/kitware/wslink
[ParaViewWeb]: https://www.paraview.org/web/
[VTK]: http://www.vtk.org/
[websocket]: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
