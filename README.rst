Postal Address
==============

Python module to parse, normalize and render postal addresses.

.. image:: https://img.shields.io/pypi/v/postal-address.svg?style=flat
    :target: https://pypi.python.org/pypi/postal-address
    :alt: Last release
.. image:: https://img.shields.io/travis/online-labs/postal-address/develop.svg?style=flat
    :target: https://travis-ci.org/online-labs/postal-address
    :alt: Unit-tests status
.. image:: https://img.shields.io/coveralls/online-labs/postal-address/develop.svg?style=flat
    :target: https://coveralls.io/r/online-labs/postal-address?branch=develop
    :alt: Coverage Status
.. image:: https://img.shields.io/requires/github/online-labs/postal-address/master.svg?style=flat
    :target: https://requires.io/github/online-labs/postal-address/requirements/?branch=master
    :alt: Requirements freshness
.. image:: https://img.shields.io/pypi/l/postal-address.svg?style=flat
    :target: https://www.gnu.org/licenses/gpl-2.0.html
    :alt: Software license
.. image:: https://img.shields.io/pypi/dm/postal-address.svg?style=flat
    :target: https://pypi.python.org/pypi/postal-address#downloads
    :alt: Popularity


Motivation
----------

    « What ties us to territory is tax. »
    -- Kevin Deldycke, 2014-11-07

The reason above is why we need fine-grained and meticulous territory
management and normalization. This project aims to solve this problem once for
all.

Don't get me wrong, this work is a huge undertaking. Postal address parsing,
normalization and rendering is hard. Much harder than you think. Please read the
famous `Falsehoods programmers believe about addresses
<http://www.mjt.me.uk/posts/falsehoods-programmers-believe-about-addresses/>`_
pamphlet.

This library is still in its early stages, but is good enough to implement
the new European Directives on VAT, which requires all e-commerce shops to
guess the locality of their EU customers depending on their billing address.


Stability policy
----------------

Here is a bunch of rules we're trying to follow regarding stability:

* Patch releases (``0.x.n`` → ``0.x.(n+1)`` upgrades) are bug-fix only. These
  releases must not break anything and keeps backward-compatibility with
  ``0.x.*`` and ``0.(x-1).*`` series.

* Minor releases (``0.n.*`` → ``0.(n+1).0`` upgrades) includes any non-bugfix
  changes. These releases must be backward-compatible with any ``0.n.*``
  version but are allowed to drop compatibility with the ``0.(n-1).*`` series
  and below.

* Major releases (``n.*.*`` → ``(n+1).0.0`` upgrades) are not planned yet:
  we're still in beta and the final feature set of the ``1.0.0`` release is not
  decided yet.


Release process
---------------

Start from the ``develop`` branch:

.. code-block:: bash

    git clone git@github.com:online-labs/postal-address.git
    git checkout develop

Update revision to its release number and update change log:

.. code-block:: bash

    vi ./postal_address/__init__.py
    vi ./CHANGES.rst

Create a release commit, tag it and merge it back to ``master`` branch:

.. code-block:: bash

    git add ./postal_address/__init__.py ./CHANGES.rst
    git commit -m "Release vXX.XX.XX"
    git tag "vXX.XX.XX"
    git push
    git push --tags
    git checkout master
    git pull
    git merge "vXX.XX.XX"
    git push

Push packaging to the test cheeseshop:

.. code-block:: bash

    python setup.py register -r testpypi
    pip install wheel
    rm -rf ./build ./dist
    python setup.py sdist bdist_egg bdist_wheel upload -r testpypi

Publish packaging to PyPi:

.. code-block:: bash

    python setup.py register -r pypi
    rm -rf ./build ./dist
    python setup.py sdist bdist_egg bdist_wheel upload -r pypi

Bump revision back to its development state:

.. code-block:: bash

    git checkout develop
    vi ./postal_address/__init__.py
    vi ./CHANGES.rst
    git add ./postal_address/__init__.py ./CHANGES.rst
    git commit -m "Post release version bump."


License
-------

This software is licensed under the `GNU General Public License v2 or later
(GPLv2+)
<https://github.com/online-labs/postal-address/blob/master/LICENSE>`_.
