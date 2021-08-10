title: Contributing
---

We welcome your contributions to the development of wslink. This document will help you with the process.

## Before You Start

Please format the code using `black` for Python and `prettier` for JavaScript. Please find below how to use them:

```
# For JavaScript
cd ./js
npm ci
npm run prettier
```

```
# For Python
black ./python
```

## Workflow

1. Fork [kitware/wslink](https://github.com/kitware/wslink).
2. Clone the repository to your computer and install dependencies.

```
$ git clone https://github.com/<username>/wslink.git
$ cd wslink/js
$ npm install
$ cd ../python
$ pip install -r requirements-dev.txt
```

3. Create a feature branch.

```
$ git checkout -b new_feature
```

4. Start hacking.
5. Test.
5. Use Commitizen for commit message

It does not matter if your changes only happened outside of the JavaScript client. Commitizen is just well integrated into JavaScript and therefore you can use it for commiting any changes.

```
$ cd ./js
$ npm run commit
```

6. Push the branch:

```
$ git push origin new_feature
```

6. Create a pull request and describe the change.

## Notice

Semantic-release [convention](https://gist.github.com/stephenparish/9941e89d80e2bc58a153) is used to write commit messages so we can automate change-log generation along with creating a new release for the JavaScript (npm) and Python (PyPI) based on your commit. No need to edit any version number, it will be automatically generated.

Unfortunately we did not managed to fully automate the testing. This means the testing will need to happen manually. Please refer to the testing checklist for running them on your system.

## Testing checklist

### Dev environment setup

```
python3 -m venv py-env
source ./py-env/bin/activate
pip install --upgrade -e ./python
```

### Build web tests

```
cd ./js
npm ci
npm run build:test
```

And

```
cd ./tests/chat-rpc-pub-sub/clients/js
npm ci
npm run build
```

### Running tests

Make sure your venv is activated (`source ./py-env/bin/activate`).

__chat-rpc-pub-sub__
```
cd ./tests/chat-rpc-pub-sub
python ./server/chat.py --port 1234 --content ./www/ --host 0.0.0.0

# Open several web clients
# => http://localhost:1234/

1. Make sure each client see the messages from any other clients
2. When n clients are connected, each message should be seen only
   once on each client.
```

__simple__
```
cd ./tests/simple
python ./server/simple.py --port 1234 --content ./www/ --host 0.0.0.0

# Open 1 web clients
# => http://localhost:1234/

Then run the following steps while having the dev console open:
1. Connect
   > WS open
2. Send Add
   > result 15
3. Send Mult
   > result 120
4. Send Image
   > result [object Blob]
   The GreenBlue Kitware logo should be visible in the page
5. Test Nesting
   In the debug console you should see `Nesting: { bytesList: [Blob, Blob], # image: { blob: Blob } }
6. Sub/Unsub
   > result [object Object]
   You should see the picture toggle between GreenBlue / ~RedPurple
7. Sub/Unsub
   > result [object Object]
   The picture update should stop
8. Mistake
   > error: -32601, "Unregistered method called", myprotocol.mistake.TYPO
9. Test NaN
   > result Infinity,NaN,-Infinity
10. Disconnect
11. Connect
    Redo 2-9
12. Server Quit
    Make sure the console running the server does not have any error
```

## Updating Documentation

The wslink documentation is part of the code repository. Feel free to update any guide `./documentation/content/docs/*.md`.

wslink's webpages are on [Github Pages](https://kitware.github.io/wslink/) and are generated using [kw-doc](https://github.com/Kitware/kw-doc). It should be automatically updated by our CI when a commit is made to the master branch. To test what website will look locally, follow those steps:

* `cd js/`
* `npm run doc:www`
    * test the docs locally

## Reporting Issues

When you encounter some problems when using wslink, you can ask me on [GitHub](https://github.com/kitware/wslink/issues). If you can't find the answer, please report it on GitHub.
