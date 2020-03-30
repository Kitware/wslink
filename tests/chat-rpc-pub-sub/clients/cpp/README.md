# Chat Client

C++ implementation of client for the chat server example for wslink.

## How to build

Create an adjacent directory by `wslink` named for example `wslink-build` and 
from there issue the following command:

```sh
cmake ../wslink/tests/chat-rpc-pub-sub/clients/cpp/

make 
```

## How to run

### Python server

If you have `wslink` installed on your python distribution you can run
the following command:

```sh
python ./server/server.py --content ./www --port 8080
```

You can also use `ParaView/pvpython` to run the same command so you don't have
to worry about Python and wslink availability.

### Our C++ client

Run the binary previous compiled:

```sh
./cli_test 

"publish:wslink.communication.channel:0" -> "Nice to meet you"
"publish:wslink.communication.channel:0" -> "What's your name?"
hello
"publish:wslink.communication.channel:0" -> "py server: hello"     

```
![demo](demo.gif)
