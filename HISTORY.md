## Release History

### 2.1.1 (2019-07-05)
* Re-release around pypi version conflict

### 2.1.0 (2019-07-05)
* Add support for ansible-2.8
* Test and lint cleanup
* Pytest 4 compliance

### 2.0.2 (2018-10-30)
* Additional fixes in support of python-3

### 2.0.1 (2018-08-10)

* Convert AdHocResult.values() to return a list, not a generator (Thanks Alan Rominger)
* Preliminary support for py3

### 2.0.0 (2017-07-27)

* Major changes to allow ansible-style inventory indexing
* Improved results processing using python objects, rather than dictionaries

### 1.4.0 (2016-MM-DD)

* Add parameter --ansible-module-path (thanks David Barroso)
* Raise DeprecationWarnings for scope=class fixtures

### 1.3.1 (2016-01-22)

* Correctly handle ansible become options

### 1.3.0 (2016-01-20)

* Add support for ansible-2.0

### 1.2.5 (2015-04-20)

* Only validate --ansible-* parameters when using pytest-ansible fixture
* Include --ansible-user when running module

### 1.2.4 (2015-03-18)

* Add ansible-1.9 privilege escalation support

### 1.2.3 (2015-03-03)

* Resolve setuptools import failure by migrating from a module to a package

### 1.2.2 (2015-03-03)

* Removed py module dependency
* Add HISTORY.md

### 1.2.1 (2015-03-02)

* Use pandoc to convert existing markdown into pypi friendly rst

### 1.2 (2015-03-02)

* Add `ansible_host` and `ansible_group` parametrized fixture
* Add cls level fixtures for users needing scope=class fixtures
* Updated examples to match new fixture return value
* Alter fixture return data to more closely align with ansible
* Raise `AnsibleHostUnreachable` whenever hosts are ... unreachable
* Set contacted and dark hosts in ConnectionError

### 1.1 (2015-02-16)

* Initial release
