title: Documentation
---

Wslink is a library that allows useful communication between a JavaScript
client and an Python web-server over websockets.

## Installation

It only takes few minutes to set up wslink. If you encounter a problem and can't find the solution here, please [submit a GitHub issue](https://github.com/kitware/wslink/issues).

### Requirements

Installing wslink as a dependency inside your Web project is quite easy. However, you do need to have a couple of other things installed first:

- [Node.js](http://nodejs.org/)
- [Git](http://git-scm.com/)

If your computer already has these, congratulations! Just install ParaViewWeb wslink with npm:

``` bash
$ npm install wslink --save
```

If not, please follow the following instructions to install all the requirements.

{% note warn For Mac users %}
You may encounter some problems when compiling. Please install Xcode from the App Store first. After Xcode is installed, open Xcode and go to **Preferences -> Download -> Command Line Tools -> Install** to install command line tools.
{% endnote %}

### Install Git

- Windows: Download & install [git](https://git-scm.com/download/win).
- Mac: Install it with [Homebrew](http://mxcl.github.com/homebrew/), [MacPorts](http://www.macports.org/) or [installer](http://sourceforge.net/projects/git-osx-installer/).
- Linux (Ubuntu, Debian): `sudo apt-get install git-core`
- Linux (Fedora, Red Hat, CentOS): `sudo yum install git-core`

### Install Node.js

The best way to install Node.js is with [nvm](https://github.com/creationix/nvm).

Once nvm is installed, restart the terminal and run the following command to install Node.js.

``` bash
$ nvm install 6
```

Alternatively, download and run [node](http://nodejs.org/).

### Install wslink

This is useful if you want to embed wslink within your own application or just use some wslink components. 

``` bash
$ npm install wslink --save
```

### Getting wslink source code for contributing

``` bash
$ git clone https://github.com/kitware/wslink.git
$ cd wslink/js
$ npm install
$ npm run build
```
