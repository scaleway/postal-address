#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2015 Scaleway and Contributors. All Rights Reserved.
#                         Kevin Deldycke <kdeldycke@scaleway.com>
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import codecs
import os
import re

from setuptools import setup, find_packages


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
    license='GPLv2+',

    install_requires=[
        'awesome-slugify',
        'pycountry >= 1.9',
    ],

    packages=find_packages(),

    tests_require=[],
    test_suite=MODULE_NAME + '.tests',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Localization',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],

    entry_points={
        'console_scripts': [],
    }
)
