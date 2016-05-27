Postal Address
==============

Python module to parse, normalize and render postal addresses.

Stable release: |release| |license| |dependencies| |popularity|

Development: |build| |quality| |coverage|

.. |release| image:: https://img.shields.io/pypi/v/postal-address.svg?style=flat
    :target: https://pypi.python.org/pypi/postal-address
    :alt: Last release
.. |license| image:: https://img.shields.io/pypi/l/postal-address.svg?style=flat
    :target: http://opensource.org/licenses/BSD-2-Clause
    :alt: Software license
.. |popularity| image:: https://img.shields.io/pypi/dm/postal-address.svg?style=flat
    :target: https://pypi.python.org/pypi/postal-address#downloads
    :alt: Popularity
.. |dependencies| image:: https://img.shields.io/requires/github/scaleway/postal-address/master.svg?style=flat
    :target: https://requires.io/github/scaleway/postal-address/requirements/?branch=master
    :alt: Requirements freshness
.. |build| image:: https://img.shields.io/travis/scaleway/postal-address/develop.svg?style=flat
    :target: https://travis-ci.org/scaleway/postal-address
    :alt: Unit-tests status
.. |coverage| image:: https://codecov.io/github/scaleway/postal-address/coverage.svg?branch=develop
    :target: https://codecov.io/github/scaleway/postal-address?branch=develop
    :alt: Coverage Status
.. |quality| image:: https://img.shields.io/scrutinizer/g/scaleway/postal-address.svg?style=flat
    :target: https://scrutinizer-ci.com/g/scaleway/postal-address/?branch=develop
    :alt: Code Quality


Motivation
----------

    « What ties us to territory is tax. »
    -- Kevin Deldycke, 2014-11-07

The reason above is why we need fine-grained and meticulous territory
management and normalization. This project aims to solve this problem once for
all.

Don't get me wrong, this work is a huge undertaking. Postal address parsing,
normalization and rendering is hard. Much `harder than you think 
<https://twitter.com/loriskumo/status/735851511331356672>`_. Please read the
famous `Falsehoods programmers believe about addresses
<http://www.mjt.me.uk/posts/falsehoods-programmers-believe-about-addresses/>`_
pamphlet.

This library is still in its early stages, but is good enough to implement
the new European Directives on VAT, which requires all e-commerce shops to
guess the locality of their EU customers depending on their billing address.


Install
-------

This package is `available on PyPi
<https://pypi.python.org/pypi/postal-address>`_, so you can install the latest
stable release and its dependencies with a simple `pip` call:

.. code-block:: bash

    $ pip install postal-address


Development
-----------

Check out latest development branch:

.. code-block:: bash

    $ git clone git@github.com:scaleway/postal-address.git
    $ cd ./postal-address
    $ python ./setup.py develop

Run unit-tests:

.. code-block:: bash

    $ python ./setup.py nosetests

Run `PEP8 <https://pep8.readthedocs.org>`_ and `Pylint
<http://docs.pylint.org>`_ code style checks:

.. code-block:: bash

    $ pip install pep8 pylint
    $ pep8 postal-address
    $ pylint --rcfile=setup.cfg postal-address


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

    $ git clone git@github.com:scaleway/postal-address.git
    $ git checkout develop

Revision should already be set to the next version, so we just need to set the
released date in the changelog:

.. code-block:: bash

    $ vi ./CHANGES.rst

Create a release commit, tag it and merge it back to ``master`` branch:

.. code-block:: bash

    $ git add ./postal_address/__init__.py ./CHANGES.rst
    $ git commit -m "Release vX.Y.Z"
    $ git tag "vX.Y.Z"
    $ git push
    $ git push --tags
    $ git checkout master
    $ git pull
    $ git merge "vX.Y.Z"
    $ git push

Push packaging to the `test cheeseshop
<https://wiki.python.org/moin/TestPyPI>`_:

.. code-block:: bash

    $ pip install wheel
    $ python ./setup.py register -r testpypi
    $ python ./setup.py clean
    $ rm -rf ./build ./dist
    $ python ./setup.py sdist bdist_egg bdist_wheel upload -r testpypi

Publish packaging to `PyPi <https://pypi.python.org>`_:

.. code-block:: bash

    $ python ./setup.py register -r pypi
    $ python ./setup.py clean
    $ rm -rf ./build ./dist
    $ python ./setup.py sdist bdist_egg bdist_wheel upload -r pypi

Bump revision back to its development state:

.. code-block:: bash

    $ pip install bumpversion
    $ git checkout develop
    $ bumpversion --verbose patch
    $ git add ./postal_address/__init__.py ./CHANGES.rst
    $ git commit -m "Post release version bump."
    $ git push

Now if the next revision is no longer bug-fix only:

.. code-block:: bash

    $ bumpversion --verbose minor
    $ git add ./postal_address/__init__.py ./CHANGES.rst
    $ git commit -m "Next release no longer bug-fix only. Bump revision."
    $ git push


License
-------

This software is licensed under the `BSD 2-Clause License
<https://github.com/scaleway/postal-address/blob/develop/LICENSE.rst>`_.
