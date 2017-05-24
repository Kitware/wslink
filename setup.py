#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
# import shutil
import sys
# import itertools

from setuptools import setup, find_packages
# from setuptools.command.install import install
# from distutils.dir_util import copy_tree

with open('README.md') as f:
    readme = f.read()

install_reqs = [
    'autobahn',
    'Twisted'
]

init = os.path.join(os.path.dirname(__file__), 'server', 'wslink', '__init__.py')
with open(init) as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(), re.MULTILINE).group(1)

# perform the install
setup(
    name='wslink',
    version=version,
    description='Python/JavaScript library for communicating over WebSocket',
    long_description=readme,
    author='Kitware, Inc.',
    author_email='kitware@kitware.com',
    url='https://github.com/kitware/wslink',
    license='BSD License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='websocket javascript rpc pubsub',
    packages=find_packages('server',
        exclude=('tests.*', 'tests', '*.plugin_tests.*', '*.plugin_tests')
    ),
    package_dir={'':'server'},
    install_requires=install_reqs,
    # extras_require=extras_reqs,
)
