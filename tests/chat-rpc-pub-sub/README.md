# Chat

This is a test application that illustrate how to setup a Python server with a Web Client along with a C++ client.

## Python server

If you have `wslink` installed on your python you can run the following command

```sh
$ python ./server/server.py --content ./www --port 8080
```

## Web client

```sh
$ cd clients/js
$ npm install
$ npm run build
```

Then open your browser on `http://localhost:8080/`

## C++ client

...todo...
