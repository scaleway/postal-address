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

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals
)

import io
import re
from os import path

from setuptools import find_packages, setup

MODULE_NAME = 'postal_address'
PACKAGE_NAME = MODULE_NAME.replace('_', '-')

DEPENDENCIES = [
    'boltons',
    'Faker >= 0.7.4',
    # TODO: subdivision definitions are broken for Czech Republic starting with
    # PyCountry 16.11.27. See:
    # https://bitbucket.org/flyingcircus/pycountry/issues/13389
    'pycountry >= 16.11.08, < 16.11.27',
]

EXTRA_DEPENDENCIES = {
    # Extra dependencies are made available through the
    # `$ pip install .[keyword]` command.
    'docs': [
        'sphinx >= 1.4',
        'sphinx_rtd_theme'],
    'tests': [
        'coverage',
        'nose',
        'pycodestyle >= 2.1.0',
        'pylint'],
    'develop': [
        'bumpversion',
        'isort',
        'readme_renderer',
        'setuptools >= 24.2.1'
        'wheel'],
}


def read_file(*relative_path_elements):
    """ Return content of a file relative to this ``setup.py``. """
    file_path = path.join(path.dirname(__file__), *relative_path_elements)
    return io.open(file_path, encoding='utf8').read().strip()


# Cache fetched version.
_version = None  # noqa


def version():
    """ Extracts version from the ``__init__.py`` file at the module's root.

    Inspired by: https://packaging.python.org/single_source_version/
    """
    global _version
    if _version:
        return _version
    init_file = read_file(MODULE_NAME, '__init__.py')
    matches = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', init_file, re.M)
    if not matches:
        raise RuntimeError("Unable to find version string in __init__.py .")
    _version = matches.group(1)  # noqa
    return _version


def latest_changes():
    """ Extract part of changelog pertaining to version. """
    lines = []
    for line in read_file('CHANGES.rst').splitlines():
        if line.startswith('-------'):
            if len(lines) > 1:
                lines = lines[:-1]
                break
        if lines:
            lines.append(line)
        elif line.startswith("`{} (".format(version())):
            lines.append(line)
    if not lines:
        raise RuntimeError(
            "Unable to find changelog for the {} release.".format(version()))
    # Renormalize and clean lines.
    return '\n'.join(lines).strip().split('\n')


def long_description():
    """ Collates project README and latest changes. """
    changes = latest_changes()
    changes[0] = "`Changes for v{}".format(changes[0][1:])
    changes[1] = '-' * len(changes[0])
    return "\n\n\n".join([
        read_file('README.rst'),
        '\n'.join(changes),
        "`Full changelog <https://{}.readthedocs.io/en/develop/changelog.html"
        "#changelog>`_.".format(PACKAGE_NAME),
    ])


setup(
    name=PACKAGE_NAME,
    version=version(),
    description="Parse, normalize and render postal addresses.",
    long_description=long_description(),
    keywords=['address', 'l10n', 'i18n'],

    author='Scaleway',
    author_email='opensource@scaleway.com',
    url='https://github.com/scaleway/postal-address',
    license='BSD',

    packages=find_packages(),
    # https://www.python.org/dev/peps/pep-0345/#version-specifiers
    python_requires='>= 2.7, != 3.0.*, != 3.1.*, != 3.2.*',
    install_requires=DEPENDENCIES,
    tests_require=DEPENDENCIES + EXTRA_DEPENDENCIES['tests'],
    extras_require=EXTRA_DEPENDENCIES,
    dependency_links=[
    ],
    test_suite='{}.tests'.format(MODULE_NAME),

    classifiers=[
        # See: https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        # List of python versions and their support status:
        # https://en.wikipedia.org/wiki/CPython#Version_history
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
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
