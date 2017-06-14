title: Contributing
---

We welcome your contributions to the development of wslink. This document will help you with the process.

## Before You Start

Please follow the coding style:

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).
- Use soft-tabs with a two space indent.
- Don't put commas first.

## Workflow

1. Fork [kitware/wslink](https://github.com/kitware/wslink).
2. Clone the repository to your computer and install dependencies.

    {% code %}
    $ git clone https://github.com/<username>/wslink.git
    $ cd wslink
    $ npm install
    $ npm install -g commitizen
    {% endcode %}

3. Create a feature branch.

    {% code %}
    $ git checkout -b new_feature
    {% endcode %}

4. Start hacking.
5. Use Commitizen for commit message

    {% code %}
    $ git cz
    {% endcode %}

6. Push the branch:

    {% code %}
    $ git push origin new_feature
    {% endcode %}

6. Create a pull request and describe the change.

## Notice

- Don't modify the version number in `package.json`. It is modified automatically.
- Your pull request will only get merged when tests have passed. Don't forget to run tests before submission.

    {% code %}
    $ npm test
    {% endcode %}

## Updating Documentation

The wslink documentation is part of the code repository.

## Reporting Issues

When you encounter some problems when using wslink, you can ask me on [GitHub](https://github.com/kitware/wslink/issues). If you can't find the answer, please report it on GitHub.
