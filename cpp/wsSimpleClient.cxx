
#include "wsSimpleClient.h"
#include "wsWebsocketConnection.h"

wsSimpleClient::wsSimpleClient()
{
  this->Connection = nullptr;
}

bool wsSimpleClient::Initialize(
  std::string const &host,
  std::string const &port,
  std::string const &target)
{
  this->Connection = new  wsWebsocketConnection("vtkweb-secret");
  if (!this->Connection->connect(host, port, target))
  {
    this->Connection->GetErrorText(this->ErrorText);
    delete this->Connection;
    this->Connection = nullptr;
    return false;
  }
  return true;
}

wsSimpleClient::~wsSimpleClient()
{
  if (!this->Connection->close())
  {
    this->Connection->GetErrorText(this->ErrorText);
  }
  delete this->Connection;
}

bool wsSimpleClient::EnableDebugging()
{
  this->Connection->DebugOn();
  return true;
}

bool wsSimpleClient::DeleteDataSet(int input)
{
  json args =
  {
    {"proxyId", input}
  };
  json result;
  if (!this->Connection->send("pv.proxy.manager.delete", &result, nullptr, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }
  if (result.count("result") && result["result"].count("success"))
  {
    return true;
  }
  if (result.count("error"))
  {
    this->ErrorText = result["error"].dump(4);
  }
  return false;
}

bool wsSimpleClient::GetDataSetInformation(int input, std::string &info)
{
  json args =
  {
    {"proxyId", input}
  };
  json result;
  if (!this->Connection->send("pv.proxy.manager.get", &result, nullptr, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }
  if (result.count("result") && result["result"].count("id"))
  {
    info = result["result"].dump(4);
    return true;
  }
  if (result.count("error"))
  {
    this->ErrorText = result["error"].dump(4);
  }
  return false;
}

bool wsSimpleClient::ListFileNames(std::vector<std::string> &files)
{
  files.clear();
  json result;
  if (!this->Connection->send("file.server.directory.list", &result))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }
  if (result.count("result") && result["result"].count("files"))
  {
    for (auto &ele : result["result"]["files"])
    {
      files.push_back(ele["label"]);
    }
    return true;
  }
  if (result.count("error"))
  {
    this->ErrorText = result["error"].dump(4);
  }
  return false;
}

bool wsSimpleClient::Send(
  std::string const &method,
  std::string const &arguments,
  std::string const &kwarguments,
  std::string &response)
{
  json result;
  json *args = nullptr;
  if (arguments.length())
  {
    args = &(json::parse(arguments));
  }
  json *kwargs = nullptr;
  if (kwarguments.length())
  {
    kwargs = &(json::parse(kwarguments));
  }
  if (!this->Connection->send(method, &result, args, kwargs))
  {
    this->Connection->GetErrorText(this->ErrorText);
    delete args;
    delete kwargs;
    return false;
  }
  delete args;
  delete kwargs;
  response = result.dump(4);
  if (result.count("error"))
  {
    this->ErrorText = result["error"].dump(4);
    return false;
  }
  return true;
}

bool wsSimpleClient::LoadDataSet(
  std::string const &dsname,
  int &ref)
{
  json args =
  {
    {"relativePath", dsname}
  };
  json result;
  if (!this->Connection->send("pv.proxy.manager.create.reader", &result, nullptr, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }
  if (result.count("result") && result["result"].count("success"))
  {
    ref = atoi(result["result"]["id"].get<std::string>().c_str());
    return true;
  }
  if (result.count("error"))
  {
    this->ErrorText = result["error"].dump(4);
  }
  return false;
}

namespace {
bool UpdateProxyList(wsWebsocketConnection *connection, json &result)
{
  json args = {-1};
  result.clear();
  if (!connection->send("pv.proxy.manager.list", &result, &args))
  {
    return false;
  }
  if (result.count("result") && result["result"].count("view"))
  {
    return true;
  }
  return false;
}
}

bool wsSimpleClient::ColorDataSetByField(
  int inputID,
  std::string const &field,
  bool useCellData,
  int component
  )

{
  json list;
  if (!UpdateProxyList(this->Connection, list))
  {
    return false;
  }

  int repID = -1;
  for (auto &a : list["result"]["sources"])
  {
    if (atoi(a["id"].get<std::string>().c_str()) == inputID)
    {
      repID = atoi(a["rep"].get<std::string>().c_str());
    }
  }

  if (repID < 0)
  {
    return false;
  }

  json args =
    {repID, "array", "POINTS", field, "Magnitude", 0, false};
  json result;
  if (!this->Connection->send("pv.color.manager.color.by", &result, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }
  if (result.count("result"))
  {
    return true;
  }
  if (result["error"])
  {
    this->ErrorText = result["error"].dump(4);
  }
  return false;
}

bool wsSimpleClient::SetVisibility(int inputID, bool val)
{
  json list;
  if (!UpdateProxyList(this->Connection, list))
  {
    return false;
  }

  int repID = -1;
  for (auto &a : list["result"]["sources"])
  {
    if (atoi(a["id"].get<std::string>().c_str()) == inputID)
    {
      repID = atoi(a["rep"].get<std::string>().c_str());
    }
  }

  if (repID < 0)
  {
    return false;
  }

  json args =
  {{
      {
        {"id", repID},
        {"name", "Visibility"},
        {"value", val ? 1 : 0 }
      }
  }};
  json result;
  if (!this->Connection->send("pv.proxy.manager.update", &result, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }

  if (result.count("error"))
  {
    this->ErrorText = result["error"].dump(4);
    return false;
  }

  return true;
}

bool wsSimpleClient::CreateProxy(const char *name, int input, int &newID)
{
  json args =
  {
    name, input, json::object(), false
  };
  json result;
  if (!this->Connection->send("pv.proxy.manager.create", &result, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }
  if (result.count("result") && result["result"].count("id"))
  {
    newID = atoi(result["result"]["id"].get<std::string>().c_str());
  }
  else
  {
    if (result.count("error"))
    {
      this->ErrorText = result["error"].dump(4);
    }
    return false;
  }
  return true;
}

bool wsSimpleClient::IsoSurface(
    int input,
    std::string const &field,
    std::vector<double> values,
    int &isoID
    )
{
  // create proxy
  if (!this->CreateProxy("Contour", input, isoID))
  {
    return false;
  }

  json contours;
  for (auto a : values)
  {
    contours.push_back(a);
  }
  json result;
  json args =
  {
    {
      {
        {"id", isoID},
        {"name", "SelectInputScalars"},
        {"value", { "POINTS", field } }
      }
    },
    {
      {
        {"id", isoID},
        {"name", "ContourValues"},
        {"value", contours }
      }
  }};
  if (!this->Connection->send("pv.proxy.manager.update", &result, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }

  return true;
}

// compute the threshold of a dataset and return it as a
// new dataset stored in result
bool wsSimpleClient::Threshold(
    int input,
    std::string const &field,
    bool fieldAssociationPoints,
    double min,
    double max,
    bool allScalars,
    int &newID
    )
{
  // create proxy
  if (!this->CreateProxy("Threshold", input, newID))
  {
    return false;
  }

  json result;
  json args =
  {
    {
      {
        {"id", newID},
        {"name", "ThresholdBetween"},
        {"value", { min, max } }
      }
    },
    {
      {
        {"id", newID},
        {"name", "SelectInputScalars"},
        {"value", { (fieldAssociationPoints ? "POINTS" : "CELLS"), field } }
      }
    },
    {
      {
        {"id", newID},
        {"name", "AllScalars"},
        {"value", allScalars }
      }
    }
  };
  if (!this->Connection->send("pv.proxy.manager.update", &result, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }

  return true;
}

// compute streamlines for a dataset and return it as a
// new dataset stored in result. The input dataset must
// have a vector field to compute streamlines. The start
// and end points define a line with numberOfSeeds seed
// points on it.
bool wsSimpleClient::StreamTracer(
  int input,
  std::string const &field,
  double const startPoint[3],
  double const endPoint[3],
  int numberOfSeeds,
  int &newID
  )
{
  // create proxy
  if (!this->CreateProxy("StreamTracer", input, newID))
  {
    return false;
  }

  json result;
  json args =
  {
    {
      {
        {"id", newID},
        {"name", "Resolution"},
        {"value", numberOfSeeds }
      }
    },
    {
      {
        {"id", newID},
        {"name", "SelectInputVectors"},
        {"value", { "POINTS", field } }
      }
    },
    {
      {
        {"id", newID},
        {"name", "Point1"},
        {"value", { startPoint[0], startPoint[1], startPoint[2]} }
      }
    },
    {
      {
        {"id", newID},
        {"name", "Point2"},
        {"value", { endPoint[0], endPoint[1], endPoint[2]} }
      }
    }
  };
  if (!this->Connection->send("pv.proxy.manager.update", &result, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }

  return true;
}

bool wsSimpleClient::GetDataAsGLTF(
  std::string &gltf
  )
{
  json args =
  {
    -1
  };
  json result;
  if (!this->Connection->send("paraview.engine.gltf.export", &result, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }
  if (result.count("result") && result["result"].count("gltf"))
  {
    gltf = result["result"]["gltf"];
    return true;
  }

  if (result.count("error"))
  {
    this->ErrorText = result["error"].dump(4);
  }
  return false;
}
