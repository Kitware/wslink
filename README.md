# wslink: websocket library between a Python server and Web client ![pypi_download](https://img.shields.io/pypi/dm/wslink)

Wslink allows easy, bi-directional communication between a python server and a
javascript or C++ client over a [websocket]. The client can make remote
procedure calls (RPC) to the server, and the server can publish messages to
topics that the client can subscribe to. The server can include binary
attachments in these messages, which are communicated as a binary websocket
message, avoiding the overhead of encoding and decoding.

## Installing

wslink can be installed with `pip wslink` or `npm install @kitware/wslink`:

## Usage for RPC and publish/subscribe

The main user of wslink is [trame](https://kitware.github.io/trame/).

- RPC - a remote procedure call that can be fired by the client and return
  sometime later with a response from the server, possibly an error.

- Publish/subscribe - client can subscribe to a topic provided by the server,
  possibly with a filter on the parts of interest. When the topic has updated
  results, the server publishes them to the client, without further action on
  the client's part.

## License

wslink is made available under the BSD 3 License. For more details, see
`LICENSE <https://github.com/Kitware/wslink/blob/master/LICENSE>`\_

## Community

`Trame <https://kitware.github.io/trame/>`_ |
`Discussions <https://github.com/Kitware/trame/discussions>`_ |
`Issues <https://github.com/Kitware/trame/issues>`_ |
`Contact Us <https://www.kitware.com/contact-us/>`_

## Examples

Some examples are provided in the `./examples/*` directory to cover the basic of
the library.

## Development

We recommend using uv for setting up and managing a virtual environment for your
development.

```
# Create venv and install all dependencies
uv sync --all-extras --dev

# Activate environment
source .venv/bin/activate

# Install commit analysis
pre-commit install
pre-commit install --hook-type commit-msg

# Allow live code edit
uv pip install -e .
```

Build client side code base

```
cd js-lib
npm install
npm run build
cd -
```

## Commit message convention

Semantic release rely on
[conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) to
generate new releases and changelog.
