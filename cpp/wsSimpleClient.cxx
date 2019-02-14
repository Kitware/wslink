
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
  this->Connection->DebugOn();
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

bool wsSimpleClient::IsoSurface(
    int input,
    std::string const &field,
    std::vector<double> values,
    int &isoID
    )
{
  json args =
  {
    "Contour", input, json::object(), false
  };
  json result;
  if (!this->Connection->send("pv.proxy.manager.create", &result, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }
  if (result.count("result") && result["result"].count("id"))
  {
    isoID = atoi(result["result"]["id"].get<std::string>().c_str());
  }
  else
  {
    if (result.count("error"))
    {
      this->ErrorText = result["error"].dump(4);
    }
    return false;
  }

  args =
  {{
      {
        {"id", isoID},
        {"name", "SelectInputScalars"},
        {"value", { "POINTS", field } }
      }
  }};
  if (!this->Connection->send("pv.proxy.manager.update", &result, &args))
  {
    this->Connection->GetErrorText(this->ErrorText);
    return false;
  }

  json contours;
  for (auto a : values)
  {
    contours.push_back(a);
  }
  args =
  {{
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
