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
normalization and rendering is hard. Much harder than you think. Please read:
http://www.mjt.me.uk/posts/falsehoods-programmers-believe-about-addresses/

This library is still in its early stages, but is good enough to implement
the new European Directives on VAT, which requires all e-commerce shops to
guess the locality of their EU customers depending on their billing address.


License
-------

This software is licensed under the `GNU General Public License v2 or later
(GPLv2+)
<https://github.com/online-labs/postal-address/blob/master/LICENSE>`_.
