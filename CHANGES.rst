ChangeLog
=========


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
