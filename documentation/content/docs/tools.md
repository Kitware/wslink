title: Tools
---

Wslink is an Open Source library for web applicatons - we welcome your
contributions!

The following guide explains our software process and the tools we use to
build and develop this library.

## Software process

We rely on Semantic-release to manage our change log, tagging and publishing
to NPM via Travis.

In order to maintain that process each commit message should follow a specific
formatting. To ensure that formating, we use Commitizen which can be triggered
via the following command line. Additional information can be found 
[here](https://gist.github.com/stephenparish/9941e89d80e2bc58a153).

    $ git cz

Then a set of questions will be presented to you like the following ones:

    $ git cz
    
    Line 1 will be cropped at 100 characters. All other lines will be wrapped
    after 100 characters.

    ? Select the type of change that you're committing: (Use arrow keys)
      feat:     A new feature
      fix:      A bug fix
      docs:     Documentation only changes
    ❯ style:    Changes that do not affect the meaning of the code
                (white-space, formatting, missing semi-colons, etc)
      refactor: A code change that neither fixes a bug or adds a feature
      perf:     A code change that improves performance
    (Move up and down to reveal more choices)

    ? Denote the scope of this change ($location, $browser, $compile, etc.):
    ESLint

    ? Write a short, imperative tense description of the change:
    Update code formatting to comply with our ESLint specification

    ? Provide a longer description of the change:

    ? List any breaking changes or issues closed by this change:

Will generate the following commit message:

    commit 1a31ecfcc2f6f4283e51187a24ce0e9d9c17ae54
    Author: Sebastien Jourdain <sebastien.jourdain@kitware.com>
    Date:   Mon Dec 21 09:29:21 2015 -0700

        style(ESLint): Update code formatting to comply with our ESLint specification


[Full convention](https://gist.github.com/stephenparish/9941e89d80e2bc58a153) 

## Code editing

[Sublime Text 3](http://www.sublimetext.com) with the following set of plugins.
To install plugins first you will have to install [Package constrol](https://packagecontrol.io/installation).

Then installing a new plugin should start with: ```Ctrl/Cmd + Shift + p``` Install

### Git + GitGutter

With GitGutter, you can see which lines have been added, deleted or modified in the gutter.

### Babel

This plugin adds proper syntax highlighting to your ES6/2015 and React JSX code.

### JsFormat

Once installed, to use JSFormat, go to your JS file and hit Ctrl + Alt + f on
Windows/Linux or Ctrl + ⌥ + f on Mac. Alternatively, use the context menu.

### Sublime-Linter + SublimeLinter-eslint

[More information available here](https://github.com/roadhump/SublimeLinter-eslint).

    $ npm install -g eslint

### EditorConfig

[More information available here](https://github.com/sindresorhus/editorconfig-sublime#readme)

## Releases

### Python

wslink is published to [pypi](https://pypi.python.org/pypi/wslink). The basic
steps taken by the maintainer to publish:

* Update version in `python/src/wslink/__init__.py`
* run tests
* `cd python/`
* `pip install -U -r requirements-dev.txt`
* `rm dist/*`
* `python setup.py bdist_wheel sdist`
* `twine upload dist/*`

### JavaScript

wslink is published to [npm](https://www.npmjs.com/package/wslink). This can
potentially be handled automatically by SemanticRelease, but we are not using
that tool (yet?) because we want to synchronize with the python release.

* `cd js/`
* `npm run build:release`
* `npm run build:example`
* `npm publish`

### Documentation

wslink's webpage is on [Github Pages](https://kitware.github.io/wslink/) and is
generated using [kw-doc](https://github.com/Kitware/kw-doc). It should be
automatically updated by Travis-CI when a commit is made to the master branch.
This is not working currently. Steps to update:

* `cd js/`
* `npm run doc:www`
    * test the docs locally
* `npm run doc:publish`
