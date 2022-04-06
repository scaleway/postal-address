Postal Address
==============

Python module to parse, normalize and render postal addresses.

Stable release: |release| |versions| |license|

Development: |docs| |coverage| |quality|

.. |release| image:: https://img.shields.io/pypi/v/postal-address.svg
    :target: https://pypi.python.org/pypi/postal-address
    :alt: Last release
.. |versions| image:: https://img.shields.io/pypi/pyversions/postal-address.svg
    :target: https://pypi.python.org/pypi/postal-address
    :alt: Python versions
.. |license| image:: https://img.shields.io/pypi/l/postal-address.svg
    :target: http://opensource.org/licenses/BSD-2-Clause
    :alt: Software license
.. |docs| image:: https://readthedocs.org/projects/postal-address/badge/?version=master
    :target: http://postal-address.readthedocs.io/en/develop/
    :alt: Documentation Status
.. |coverage| image:: https://codecov.io/gh/scaleway/postal-address/branch/develop/graph/badge.svg
    :target: https://codecov.io/github/scaleway/postal-address?branch=master
    :alt: Coverage Status
.. |quality| image:: https://scrutinizer-ci.com/g/scaleway/postal-address/badges/quality-score.png?b=develop
    :target: https://scrutinizer-ci.com/g/scaleway/postal-address/?branch=master
    :alt: Code Quality


Motivation
----------

    « What ties us to territory is tax. »
    -- Kevin Deldycke, 2014-11-07

The reason above is why we need fine-grained and meticulous territory
management and normalization. This project aims to solve this problem once for
all.

Don't get me wrong, this work is a huge undertaking. Postal address parsing,
normalization and rendering is hard. See the collection of `falsehoods
programmers believe about postal addresses
<https://github.com/kdeldycke/awesome-falsehood#postal-addresses>`_.

This library is still in its early stages, but is good enough to implement
the new European Directives on VAT, which requires all e-commerce shops to
guess the locality of their EU customers depending on their billing address.
