## Introduction

This is an interactive test that we wish to automate at some point.
But this allow to make sure the set of features we aim to support continue to work
without too much burden.

## Running the test

```
export WSLINK_ROOT=$PWD/../..

cd $WSLINK_ROOT
python3 -m venv py-env
source ./py-env/bin/activate
pip install -r ./python

cd $WSLINK_ROOT/js
npm i
npm run test
```

Open `http://localhost:8080/index.html`

Then run the following steps while having the dev console open:
1. Connect
   1. WS open
2. Send Add
   1. result 15
3. Send Mult
   1. result 120
4. Send Image
   1. result [object Blob]
   2. The GreenBlue Kitware logo should be visible in the page
5. Test Nesting
   1. In the debug console you should see `Nesting: { bytesList: [Blob, Blob], image: { blob: Blob } }
6. Sub/Unsub
   1. result [object Object]
   2. You should see the picture toggle between GreenBlue / ~RedPurple
7. Sub/Unsub
   1. result [object Object]
   2. The picture update should stop
8. Mistake
   1. error: -32601, "Unregistered method called", myprotocol.mistake.TYPO
9. Test NaN
   1. result Infinity,NaN,-Infinity
10. Disconnect
11. Connect
    1.  Redo 2-9
12. Server Quit
    1.  Make sure the console running the server does not have any error
