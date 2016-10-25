#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2016 Scaleway and Contributors. All Rights Reserved.
#                         Kevin Deldycke <kdeldycke@scaleway.com>
#                         Bastien Chatelard <bchatelard@scaleway.com>
#
# Licensed under the BSD 2-Clause License (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the
# License at http://opensource.org/licenses/BSD-2-Clause

import codecs
import os
import re

from setuptools import find_packages, setup

MODULE_NAME = 'postal_address'


def get_version():

    with open(os.path.join(
        os.path.dirname(__file__), MODULE_NAME, '__init__.py')
    ) as init:

        for line in init.readlines():
            res = re.match(r'__version__ *= *[\'"]([0-9\.]*)[\'"]$', line)
            if res:
                return res.group(1)


def get_long_description():
    readme = os.path.join(os.path.dirname(__file__), 'README.rst')
    changes = os.path.join(os.path.dirname(__file__), 'CHANGES.rst')
    return codecs.open(readme, encoding='utf-8').read() + '\n' + \
        codecs.open(changes, encoding='utf-8').read()


setup(
    name='postal-address',
    version=get_version(),
    description="Parse, normalize and render postal addresses.",
    long_description=get_long_description(),

    author='Scaleway',
    author_email='opensource@scaleway.com',
    url='http://github.com/scaleway/postal-address',
    license='BSD',

    install_requires=[
        'pycountry >= 1.9, < 2.0',
        'Faker >= 0.7.3',
        'boltons',
    ],

    packages=find_packages(),

    tests_require=[],
    test_suite=MODULE_NAME + '.tests',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Localization',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],

    entry_points={
        'console_scripts': [],
    }
)
