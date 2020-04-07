//
// Class to communicate with a ParaViewWeb server
//
// All methods return true on success
//

#if defined(_WIN32) && !defined(_WIN32_WINNT)
#define _WIN32_WINNT 0x0601  // Windows 7 or later
#endif

#define  BOOST_ALL_NO_LIB
#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/beast/websocket.hpp>
#include <boost/beast/version.hpp>
#include <boost/asio/connect.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <cstdlib>
#include <iostream>
#include <string>
#include <regex>
#include <future>
#include <mutex>
#include <queue>
#include <condition_variable>

namespace beast = boost::beast;     // from <boost/beast.hpp>
namespace http = beast::http;       // from <boost/beast/http.hpp>
namespace websocket = beast::websocket; // from <boost/beast/websocket.hpp>
namespace net = boost::asio;        // from <boost/asio.hpp>
using tcp = net::ip::tcp;           // from <boost/asio/ip/tcp.hpp>

#include <sstream>
#include <map>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

class wsLauncher
{
public:
  bool start(
    std::string const &host,
    std::string const &port,
    std::string const &target,
    json *config)
  {
    this->LauncherHost = host;
    this->LauncherTarget = target;

    // These objects perform our I/O
    tcp::resolver resolver(this->ioc);

    // Look up the domain name
    auto const results = resolver.resolve(host, port);

    boost::system::error_code ec;

    // Make the connection on the IP address we get from a lookup
    net::connect(this->socket, results.begin(), results.end(), ec);
    if (ec)
    {
      this->HandleError("connect", ec);
      return false;
    }

    // Set up an HTTP POST request message
    http::request<http::string_body> req{http::verb::post, target, 11};
    req.set(http::field::host, host);
    req.set(http::field::user_agent, BOOST_BEAST_VERSION_STRING);
    req.set(beast::http::field::content_type, "application/json");
    req.body() = config->dump();
    req.set(http::field::content_length, config->dump().length());
    req.prepare_payload();

    // Send the HTTP request to the remote host
    http::write(this->socket, req);

    // This buffer is used for reading and must be persisted
    beast::flat_buffer buffer;

    // Declare a container to hold the response
    http::response<http::string_body> res;

    // Receive the HTTP response
    http::read(this->socket, buffer, res, ec);

    // Write the message to standard out
    this->Connection = json::parse(res.body());
    if (this->Debug)
    {
      std::cerr << this->Connection.dump(4);
    }

    this->ServerTarget = this->Connection["sessionURL"];
    this->ServerHost = this->Connection["host"];
    this->ServerPort = std::to_string(this->Connection["port"].get<int>());
    this->Secret = this->Connection["secret"];
    std::string longHost = this->ServerHost + ":" + this->ServerPort;
    // now compute the target from the sessionURL
    size_t pos = this->ServerTarget.find(longHost);
    if (pos > this->ServerTarget.length())
    {
      this->ErrorText = "Unable to find target in host string " + this->ServerTarget;
      return false;
    }
    this->ServerTarget = this->ServerTarget.substr(pos + longHost.length());

    return true;
  }


  //
  // Note this method doe snot work on the python server
  // as of March 2019. Typically you shut down the server
  // by closing the websocket instead
  //
  bool stop()
  {
    // Set up an HTTP POST request message
    std::string target = this->LauncherTarget;
    target += "/";
    target += this->Connection["id"].get<std::string>();
    http::request<http::string_body> req{http::verb::delete_, target, 11};
    req.set(http::field::host, this->LauncherHost);
    req.set(http::field::user_agent, BOOST_BEAST_VERSION_STRING);
    req.set(beast::http::field::content_type, "application/json");

    std::cerr << req << "\n";

    // Send the HTTP request to the remote host
    boost::system::error_code ec;
    http::write(this->socket, req, ec);
    if (ec)
    {
      this->HandleError("send delete", ec);
      return false;
    }

    // This buffer is used for reading and must be persisted
    beast::flat_buffer buffer;

    // Declare a container to hold the response
    http::response<http::string_body> res;

    // Receive the HTTP response
    http::read(this->socket, buffer, res, ec);
    if (ec)
    {
      this->HandleError("delete", ec);
      return false;
    }
    if (this->Debug)
    {
      std::cerr << res << "\n";
    }

    // Gracefully close the socket
    this->socket.shutdown(tcp::socket::shutdown_both, ec);

    // not_connected happens sometimes
    // so don't bother reporting it.
    //
    if (ec && ec != beast::errc::not_connected)
    {
      this->HandleError("stop", ec);
      return false;
    }

    // If we get here then the connection is closed gracefully
    return true;
  }

  void fetchConnection()
  {

  }

  wsLauncher() : socket(this->ioc)
  {

  }

  bool GetErrorText(std::string &in) {
    in = this->ErrorText;
    return true;
  }

  std::string const &GetServerHost() {
    return this->ServerHost;
  }

  std::string const &GetServerPort() {
    return this->ServerPort;
  }

  std::string const &GetServerTarget() {
    return this->ServerTarget;
  }

  std::string const &GetSecret() {
    return this->Secret;
  }
  json &GetConnection() {
    return this->Connection;
  }

  void DebugOn() {
    this->Debug = true;
  }

protected:
  void HandleError(std::string const &txt, boost::system::error_code ec)
  {
    this->ErrorText = txt;
    this->ErrorText += " ";
    this->ErrorText += ec.message();
    if (this->Debug)
    {
      std::cerr << this->ErrorText << "\n";
    }
  }

  // The io_context is required for all I/O
  std::string LauncherHost;
  std::string LauncherTarget;
  std::string ServerTarget;
  std::string ServerHost;
  std::string ServerPort;

  bool Debug = false;
  net::io_context ioc;
  tcp::socket socket;
  std::string Secret;
  std::string ErrorText;
  json Connection;
};

class wsWebsocketConnection
{
public:
  using TopicCallBackType = std::function<void(const json&)>;

  wsWebsocketConnection(std::string secret) : Secret(secret) { }

  bool close()
  {
    {
      std::unique_lock<std::mutex> lock (MutexPolling);
      if (isPolling)
      {
        isPolling = false;
        ThreadPolling.join();
      }
    }
    // currently the below does not work due to
    // https://github.com/Kitware/wslink/issues/21
    // so it is commented out
    // send the exit message
    // json result;
    // this->send("application.exit", &result);

    // Send a "close" frame to the other end, this is a websocket thing
    boost::system::error_code ec;
    this->ws.close(websocket::close_code::normal, ec);
    if (ec)
    {
      this->HandleError("close", ec);
      return false;
    }
    return true;
  }

  bool connect(std::string host, std::string port, std::string target)
  {
    boost::system::error_code ec;

    // Look up the domain name
    tcp::resolver resolver{this->ioc};
    auto const results = resolver.resolve(host, port);

    // Make the connection on the IP address we get from a lookup
    net::connect(this->ws.next_layer(), results.begin(), results.end(), ec);
    if (ec)
    {
      this->HandleError("connect", ec);
      return false;
    }

    // Perform the websocket handshake
    std::string longHost = host + ":" + port;
    this->ws.handshake(longHost, target, ec);
    if (ec)
    {
      this->HandleError("handshake", ec);
      return false;
    }

    // now estalish the session
    json cmd = {
      {"wslink", "1.0"},
      {"id", "system:c0:0"},
      {"method", "wslink.hello"},
      {"args", { { { "secret", this->Secret }}}}
    };
    this->ws.write(net::buffer(cmd.dump()), ec);
    if(ec)
    {
      this->HandleError("hello", ec);
      return false;
    }

    beast::multi_buffer buffer;
    ws.read(buffer, ec);
    if(ec)
    {
      this->HandleError("read", ec);
      return false;
    }

    // Read the response and get the clientID
    if (this->Debug)
    {
      std::cout << beast::buffers_to_string(buffer.data()) << std::endl;
    }

    json result = json::parse(beast::buffers_to_string(buffer.data()));
    this->ClientID = result["result"]["clientID"];

    this->MessageCount = 1;

    if (!isPolling) {
      isPolling = true;
      ThreadPolling = std::thread(&wsWebsocketConnection::ThreadPollingFn, this);
    }

    return true;
  }

  // return true on success
  bool send(std::string method, json *result, json *args = nullptr, json *kwargs = nullptr)
  {
    std::ostringstream os;
    os << "rpc:" << this->ClientID << ":" << this->MessageCount;

    // Write json.
    json cmd = {
      {"wslink", "1.0"},
      {"id", os.str()},
      {"method", method}
    };

    if (args)
    {
      cmd["args"] = *args;
    }
    if (kwargs)
    {
      cmd["kwargs"] = *kwargs;
    }

    // Send the message
    boost::system::error_code ec;
    this->ws.write(net::buffer(cmd.dump(4)), ec);
    if(ec)
    {
      this->HandleError("send", ec);
      return false;
    }

    if (result)
    {
      std::unique_lock<std::mutex> lock (MutexRPCMessages);
      while (QueueRPCMessages.empty()) {
        CVRPCMessages.wait(lock);
      }

      *result = QueueRPCMessages.front();
      QueueRPCMessages.pop();
    }

    return true;
  }

  // return true on success
  bool subscribe(std::string topic, TopicCallBackType callback)
  {
    std::unique_lock<std::mutex> lock (MutexSubscriptions);
    this->Subscriptions[topic] = callback;
    return true;
  }

  // return true on success
  bool unsubscribe(std::string topic)
  {
    std::unique_lock<std::mutex> lock (MutexSubscriptions);
    Subscriptions.erase(topic);
    return true;
  }

  // enable debugging output
  bool DebugOn() {
    this->Debug = true;
    return true;
  }

  bool GetErrorText(std::string &in) {
    in = this->ErrorText;
    return true;
  }

protected:
  void HandleError(std::string const &txt, boost::system::error_code ec) {
    this->ErrorText = txt;
    this->ErrorText += " ";
    this->ErrorText += ec.message();
    if (this->Debug)
    {
      std::cerr << this->ErrorText << "\n";
    }
  }

  void ThreadPollingFn()
  {
    while (isPolling)
    {
      beast::multi_buffer buffer;
      boost::system::error_code ec;
      this->ws.read(buffer, ec);

      if(ec)
      {
        this->HandleError("read", ec);
        continue;
      }

      auto result = json::parse(beast::buffers_to_string(buffer.data()));

      if (this->Debug)
      {
        std::cout << beast::buffers_to_string(buffer.data()) << std::endl;
      }

      std::string id = result["id"];

      std::regex e ("^(rpc|publish|system):([a-z0-1A-Z.]+):(?:\\d+)$");
      std::smatch matches;
      std::regex_match(id, matches, e);

      if (matches.size() >= 3)
      {
        std::string type = matches[1];
        std::string topic = matches[2];

        if (type == "publish")
        {
          decltype(Subscriptions)::iterator it;
          {
            std::unique_lock<std::mutex> lock (MutexSubscriptions);
            it = Subscriptions.find(topic);
          }

          if (it != Subscriptions.end())
          {
            it->second(result);
          }
        }
        else if (type == "rpc")
        {
          std::unique_lock<std::mutex> lock (MutexRPCMessages);
          QueueRPCMessages.push(result);
          CVRPCMessages.notify_all();

        } else {
          std::cerr << "unsupported type of message: " << type << std::endl;
        }

        this->MessageCount++;
      }
    }
  }

  // The io_context is required for all I/O
  net::io_context ioc;
  websocket::stream<tcp::socket> ws{ioc};
  std::string Secret;
  std::string ClientID;
  unsigned int MessageCount = 0;
  bool Debug = false;
  bool isPolling = false;
  std::string ErrorText;

  std::unordered_map<std::string, TopicCallBackType> Subscriptions;
  std::mutex MutexSubscriptions;
  std::mutex MutexPolling;
  std::mutex MutexRPCMessages;
  std::condition_variable CVRPCMessages;
  std::thread ThreadPolling;
  std::queue<json> QueueRPCMessages;
};
