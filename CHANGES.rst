ChangeLog
=========


0.4.4 (unreleased)
------------------

* No changes yet.


0.4.3 (2015-03-26)
------------------

* Fix rendering of subdivision-less addresses.


0.4.2 (2015-03-26)
------------------

* Fix ``country_code`` to ``subdivision_code`` validation if the latter is not
  set.


0.4.1 (2015-03-26)
------------------

* Base our custom ``InvalidAddress`` exception on ``ValueError`` to increase
  backward compatibility.


0.4.0 (2015-03-25)
------------------

* Show subdivision as-is in rendered address if not already printed by state,
  country or city.
* Document stability policy. Closes #8.
* Change internals to refer to address components as ``fields``.
* Raise custom exception on address validation a detailed list of invalid
  fields in one go. Closes #7.


0.3.3 (2015-03-25)
------------------

* Fix bad released version.


0.3.2 (2015-03-25)
------------------

* Add backward compatibility to the ``0.2`` series following territory utils
  split out of the ``address`` module. See #8 and #9.


0.3.1 (2015-03-05)
------------------

* Fix rendering of state in address.


0.3.0 (2015-03-04)
------------------

* Remove backward compatibility with 0.1.0.
* Allow direct import of classes from module root.
* Split territory utils out to their own file. See #3.
* Rename ``normalize_country_code`` to ``country_from_subdivision``. Mark the
  former as deprecated.
* Address normalization is now non-blocking. It simply reset invalid components
  to None. Only a call to ``validate`` method check data consistency.


0.2.1 (2014-12-22)
------------------

* Push a new release to fix cached desynced packages on cheeseshops and clones.


0.2.0 (2014-12-18)
------------------

* Package the whole module for proper distribution.


0.1.1 (2014-12-16)
------------------

* Restore partial backward compatibility with address module from 0.1.0.


0.1.0 (2014-12-15)
------------------

* First public release.


0.0.0 (2013-12-06)
------------------

* First commit.
