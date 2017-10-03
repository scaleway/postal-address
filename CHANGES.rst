ChangeLog
=========


`1.3.5 (2017-10-03) <https://github.com/scaleway/postal-address/compare/v1.3.4...v1.3.5>`_
------------------------------------------------------------------------------------------

* Exclude production of invalid random addresses in ``ar_PS`` locale. See #20.
* Bump dependency to ``Faker >= 0.8.4``.


`1.3.4 (2017-09-29) <https://github.com/scaleway/postal-address/compare/v1.3.3...v1.3.4>`_
------------------------------------------------------------------------------------------

* Restrict ``Faker`` to ``0.8.3`` as the next release seems to mess up
  production of territory subdivisions. See #19 and #22.
* Add cache on ``supported_*_codes()`` functions.


`1.3.3 (2016-12-20) <https://github.com/scaleway/postal-address/compare/v1.3.2...v1.3.3>`_
------------------------------------------------------------------------------------------

* Re-allow production of random addresses in ``no_NO`` and ``fa_IR`` locales.
* Bump dependency to ``Faker >= 0.7.7``.


`1.3.2 (2016-12-20) <https://github.com/scaleway/postal-address/compare/v1.3.1...v1.3.2>`_
------------------------------------------------------------------------------------------

* Exclude production of invalid random addresses in ``fa_IR`` locale.


`1.3.1 (2016-12-20) <https://github.com/scaleway/postal-address/compare/v1.3.0...v1.3.1>`_
------------------------------------------------------------------------------------------

* Fix selection of random locale in ``random_address()``.
* Bump dependency to ``Faker >= 0.7.4``.
* Exclude production of invalid random addresses in ``no_NO`` locale.
* Fix rendering of changelog link in RST.


`1.3.0 (2016-11-29) <https://github.com/scaleway/postal-address/compare/v1.2.0...v1.3.0>`_
------------------------------------------------------------------------------------------

* Build documentation via Sphinx. Closes #14.
* Move development and packaging documentation to Sphinx.
* Restrict ``pycountry`` to ``16.11.8`` release because of bad Czech Republic
  subdivision definitions.
* Remove popularity badge: PyPI download counters are broken and no longer
  displayed.
* Move coverage config to ``setup.cfg``.
* Add ``test`` and ``develop`` dependencies.
* Only show latest changes in the long description of the package instead of
  the full changelog.
* Replace ``pep8`` package by ``pycodestyle``.
* Enforce ``pycodestyle`` checks in Travis CI jobs.
* Test production of packages in Travis CI jobs.
* Always check for package metadata in Travis CI jobs.
* Make wheels generated under Python 2 environnment available for Python 3 too.
* Add link to full changelog in package's long description.


`1.2.0 (2016-11-14) <https://github.com/scaleway/postal-address/compare/v1.1.2...v1.2.0>`_
------------------------------------------------------------------------------------------

* Change internal structure of ``InvalidAddress`` exception to print invalid
  field values in error message.
* Update ``pycountry`` to the new calendar-versionned series.
* Allow unittests failure on PyPy3.


`1.1.2 (2016-10-25) <https://github.com/scaleway/postal-address/compare/v1.1.1...v1.1.2>`_
------------------------------------------------------------------------------------------

* Keeps ``pycountry`` dependency to the 1.x series.


`1.1.1 (2016-09-21) <https://github.com/scaleway/postal-address/compare/v1.1.0...v1.1.1>`_
------------------------------------------------------------------------------------------

* Replace dependency on ``fake-factory`` by ``Faker``.
* Add inactive unittests to highlight un-caught edge-cases in the country/state
  normalization code on derivation from subdivisions. Refs #16.


`1.1.0 (2016-05-27) <https://github.com/scaleway/postal-address/compare/v1.0.0...v1.1.0>`_
------------------------------------------------------------------------------------------

* Remove deprecated ``random_word()``, ``random_phrase()`` and
  ``random_postal_code()``.
* Activate tests on Python 3.3.
* Allow production of random chinese addresses.
* Bump ``faker`` requirement to 0.5.4.
* Activate tests on PyPy and PyPy3.


`1.0.0 (2016-02-25) <https://github.com/scaleway/postal-address/compare/v0.9.1...v1.0.0>`_
------------------------------------------------------------------------------------------

* Add a new ``territory_children_codes()`` utility to fetch all children of a
  territory.
* Use ``faker`` module to produce fuzzier random addresses.
* Deprecate ``random_word()``, ``random_phrase()`` and
  ``random_postal_code()`` in favor of ``faker`` module.
* Add ``isort`` configuration.
* Only allow string-like types to be set on editable address fields.
* Replace ``awesome-slugify`` dependency by ``boltons``.
* Activate tests on Python 3.5.


`0.9.1 (2015-11-23) <https://github.com/scaleway/postal-address/compare/v0.9.0...v0.9.1>`_
------------------------------------------------------------------------------------------

* Switch from ``coveralls.io`` to ``codecov.io``.


`0.9.0 (2015-09-17) <https://github.com/scaleway/postal-address/compare/v0.8.1...v0.9.0>`_
------------------------------------------------------------------------------------------

* Change license from GPLv2+ to BSD 2-Clause license. Closes #13.
* Add bumpversion configuration.
* Add custom PEP8 and PyLint configuration.


`0.8.1 (2015-06-01) <https://github.com/scaleway/postal-address/compare/v0.8.0...v0.8.1>`_
------------------------------------------------------------------------------------------

* Fix bad released version.


`0.8.0 (2015-06-01) <https://github.com/scaleway/postal-address/compare/v0.7.2...v0.8.0>`_
------------------------------------------------------------------------------------------

* Normalize all white spaces, not only leadings and trailings.
* Test that the ``Address`` object is able to digest unicode messs.
* Normalize postal codes to uppercase alphanumerics with spaces and hyphens.
  Refs #2.


`0.7.2 (2015-05-26) <https://github.com/scaleway/postal-address/compare/v0.7.1...v0.7.2>`_
------------------------------------------------------------------------------------------

* Fix encoding of ``README`` and ``CHANGES``. Closes #12.


`0.7.1 (2015-05-20) <https://github.com/scaleway/postal-address/compare/v0.7.0...v0.7.1>`_
------------------------------------------------------------------------------------------

* Add utility method to generate random addresses for test mockups.


`0.7.0 (2015-04-14) <https://github.com/scaleway/postal-address/compare/v0.6.1...v0.7.0>`_
------------------------------------------------------------------------------------------

* Include internal fields disguised as properties when ``repr``-ing the
  ``Address`` object.
* Always use the common name of a country if available instead of its official
  default value.


`0.6.1 (2015-04-07) <https://github.com/scaleway/postal-address/compare/v0.6.0...v0.6.1>`_
------------------------------------------------------------------------------------------

* Update all Online Labs references to Scaleway.


`0.6.0 (2015-04-02) <https://github.com/scaleway/postal-address/compare/v0.5.2...v0.6.0>`_
------------------------------------------------------------------------------------------

* Add an option to bypass ``Address``' strict normalization.


`0.5.2 (2015-03-30) <https://github.com/scaleway/postal-address/compare/v0.5.1...v0.5.2>`_
------------------------------------------------------------------------------------------

* Always sort fields in error messages to improve reproducibility when
  unit testing.
* Deduplicate inconsistent field entries in custom address exception.


`0.5.1 (2015-03-30) <https://github.com/scaleway/postal-address/compare/v0.5.0...v0.5.1>`_
------------------------------------------------------------------------------------------

* Fix bad released version.


`0.5.0 (2015-03-30) <https://github.com/scaleway/postal-address/compare/v0.4.3...v0.5.0>`_
------------------------------------------------------------------------------------------

* Increase capabilities of alias resolution by ``country_aliases()`` method,
  which in turns increase address normalization efficiency.
* Remove backward compatibility with ``0.3`` series.
* Remove deprecated ``territory.territory_tree()`` method which provided
  backward compatibilityi with the ``0.1`` series. It should have been removed
  in the ``0.3.0`` release.
* Split-up ``supported_territory_codes()`` into ``supported_country_codes()``
  and ``supported_subdivision_codes()``.


`0.4.3 (2015-03-26) <https://github.com/scaleway/postal-address/compare/v0.4.2...v0.4.3>`_
------------------------------------------------------------------------------------------

* Fix rendering of subdivision-less addresses.


`0.4.2 (2015-03-26) <https://github.com/scaleway/postal-address/compare/v0.4.1...v0.4.2>`_
------------------------------------------------------------------------------------------

* Fix ``country_code`` to ``subdivision_code`` validation if the latter is not
  set.


`0.4.1 (2015-03-26) <https://github.com/scaleway/postal-address/compare/v0.4.0...v0.4.1>`_
------------------------------------------------------------------------------------------

* Base our custom ``InvalidAddress`` exception on ``ValueError`` to increase
  backward compatibility.


`0.4.0 (2015-03-25) <https://github.com/scaleway/postal-address/compare/v0.3.3...v0.4.0>`_
------------------------------------------------------------------------------------------

* Show subdivision as-is in rendered address if not already printed by state,
  country or city.
* Document stability policy. Closes #8.
* Change internals to refer to address components as ``fields``.
* Raise custom exception on address validation a detailed list of invalid
  fields in one go. Closes #7.


`0.3.3 (2015-03-25) <https://github.com/scaleway/postal-address/compare/v0.3.2...v0.3.3>`_
------------------------------------------------------------------------------------------

* Fix bad released version.


`0.3.2 (2015-03-25) <https://github.com/scaleway/postal-address/compare/v0.3.1...v0.3.2>`_
------------------------------------------------------------------------------------------

* Add backward compatibility to the ``0.2`` series following territory utils
  split out of the ``address`` module. See #8 and #9.


`0.3.1 (2015-03-05) <https://github.com/scaleway/postal-address/compare/v0.3.0...v0.3.1>`_
------------------------------------------------------------------------------------------

* Fix rendering of state in address.


`0.3.0 (2015-03-04) <https://github.com/scaleway/postal-address/compare/v0.2.1...v0.3.0>`_
------------------------------------------------------------------------------------------

* Remove backward compatibility with the ``0.1`` series.
* Allow direct import of classes from module root.
* Split territory utils out to their own file. See #3.
* Rename ``normalize_country_code`` to ``country_from_subdivision``. Mark the
  former as deprecated.
* Address normalization is now non-blocking. It simply reset invalid components
  to None. Only a call to ``validate`` method check data consistency.


`0.2.1 (2014-12-22) <https://github.com/scaleway/postal-address/compare/v0.2.0...v0.2.1>`_
------------------------------------------------------------------------------------------

* Push a new release to fix cached desynced packages on cheeseshops and clones.


`0.2.0 (2014-12-18) <https://github.com/scaleway/postal-address/compare/v0.1.1...v0.2.0>`_
------------------------------------------------------------------------------------------

* Package the whole module for proper distribution.


`0.1.1 (2014-12-16) <https://github.com/scaleway/postal-address/compare/v0.1.0...v0.1.1>`_
------------------------------------------------------------------------------------------

* Restore partial backward compatibility with address module from the ``0.1``
  series.


`0.1.0 (2014-12-15) <https://github.com/scaleway/postal-address/compare/v0.0.0...v0.1.0>`_
------------------------------------------------------------------------------------------

* First public release.


`0.0.0 (2013-12-06) <https://github.com/scaleway/postal-address/commit/de00e1>`_
--------------------------------------------------------------------------------

* First commit.
