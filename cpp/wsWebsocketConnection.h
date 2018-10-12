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

namespace beast = boost::beast;     // from <boost/beast.hpp>
namespace http = beast::http;       // from <boost/beast/http.hpp>
namespace websocket = beast::websocket; // from <boost/beast/websocket.hpp>
namespace net = boost::asio;        // from <boost/asio.hpp>
using tcp = net::ip::tcp;           // from <boost/asio/ip/tcp.hpp>

#include <sstream>
#include <map>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

// class wsProcessLauncher
// {
//   bool start(config)
//   {
//     // The io_context is required for all I/O
//     net::io_context ioc;

//     // These objects perform our I/O
//     tcp::resolver resolver{ioc};
//     tcp::socket socket{ioc};

//     // Look up the domain name
//     auto const results = resolver.resolve(host, port);

//     // Make the connection on the IP address we get from a lookup
//     net::connect(socket, results.begin(), results.end());

//     // Set up an HTTP GET request message
//     http::request<http::string_body> req{http::verb::post, target, version};
//     req.set(http::field::host, host);
//     req.set(http::field::user_agent, BOOST_BEAST_VERSION_STRING);

//     // Send the HTTP request to the remote host
//     http::write(socket, req);

//     // This buffer is used for reading and must be persisted
//     beast::flat_buffer buffer;

//     // Declare a container to hold the response
//     http::response<http::dynamic_body> res;

//     // Receive the HTTP response
//     http::read(socket, buffer, res);

//     // Write the message to standard out
//     std::cout << res << std::endl;

//     // Gracefully close the socket
//     beast::error_code ec;
//     socket.shutdown(tcp::socket::shutdown_both, ec);

//     // not_connected happens sometimes
//     // so don't bother reporting it.
//     //
//     if(ec && ec != beast::errc::not_connected)
//         throw beast::system_error{ec};

//     // If we get here then the connection is closed gracefully
//   }

//             // var xhr = new XMLHttpRequest(),
//     //   url = model.endPoint;

//     // xhr.open('POST', url, true);
//     // xhr.responseType = 'json';
//     // const supportsJson = 'response' in xhr && xhr.responseType === 'json';

//     // xhr.onload = (e) => {
//     //   const response = supportsJson ? xhr.response : JSON.parse(xhr.response);
//     //   if (xhr.status === 200 && response && !response.error) {
//     //     // Add connection to our global list
//     //     connections.push(response);
//     //     publicAPI.fireProcessReady(response);
//     //     return;
//     //   }
//     //   publicAPI.fireError(xhr);
//     // };

//     // xhr.onerror = (e) => {
//     //   publicAPI.fireError(xhr);
//     // };

//     // xhr.send(JSON.stringify(config));
//   }
// };

class wsWebsocketConnection
{
public:
  wsWebsocketConnection(std::string secret) : Secret(secret) {
  }

  bool close()
  {
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

  bool connect(std::string host, std::string port, std::string target) {

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
      {"args", { { { "secret", "vtkweb-secret" }}}}
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

    // Read a message into our buffer
    // This buffer will hold the incoming message
    beast::multi_buffer buffer;
    ws.read(buffer, ec);
    if(ec)
    {
      this->HandleError("read", ec);
      return false;
    }

    if (result)
    {
      *result = json::parse(beast::buffers_to_string(buffer.data()));
    }

    // The make_printable() function helps print a ConstBufferSequence
    if (this->Debug)
    {
      std::cout << beast::buffers_to_string(buffer.data()) << std::endl;
    }

    this->MessageCount++;
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

  // The io_context is required for all I/O
  net::io_context ioc;
  websocket::stream<tcp::socket> ws{ioc};
  std::string Secret;
  std::string ClientID;
  unsigned int MessageCount = 0;
  bool Debug = false;
  std::string ErrorText;
};
