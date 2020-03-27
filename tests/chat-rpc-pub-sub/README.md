# Chat

This is a test application that illustrate how to setup a Python server with a Web Client along with a C++ client.

## Python server

If you have `wslink` installed on your python you can run the following command

```sh
python ./server/server.py --content ./www --port 8080
```

Then open your browser on `http://localhost:8080/`

You can also use `ParaView/pvpython` to run the same command so you don't have to worry about Python and wslink availability.

## Web client

The following set of commands will transpile the JavaScript code and generate the `./www` directory that is served by the server process.
That bundled version has already been publish to the repository but in case you want to update or edit the code, the following commands will update that directory.

```sh
cd clients/js
npm install
npm run build
```

## C++ client

...todo...
