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

readme = ''
with open('README.rst') as f:
    readme = f.read()

install_reqs = [
    'autobahn',
    'Twisted'
]

init = os.path.join(os.path.dirname(__file__), 'src', 'wslink', '__init__.py')
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
    license='BSD-3-Clause',
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
    packages=find_packages('src',
        exclude=('tests.*', 'tests')
    ),
    package_dir={'':'src'},
    install_requires=install_reqs,
    extras_require={
        'security': ['service_identity>=17.0.0'],
    },
)
