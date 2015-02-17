pytest-ansible
==============

[![Current Version](https://pypip.in/v/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Supported Python versions](https://pypip.in/py_versions/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Downloads](https://pypip.in/d/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Build Status](https://travis-ci.org/jlaska/pytest-ansible.svg?branch=master)](https://travis-ci.org/jlaska/pytest-ansible)

This repository contains a plugin for ``py.test`` which adds several fixtures
for running ``ansible`` modules, or inspecting ``ansible_facts``.

Installation
============

This plugin gets automatically connected to ``py.test`` via ``entry point`` if installed.

Usage
=====

Once installed, the following ``py.test`` command-line parameters are available:

```bash
py.test \
    [--ansible-inventory <path_to_inventory>] \
    [--ansible-host-pattern <host-pattern>] \
    [--ansible-connection <plugin>] \
    [--ansible-user <username>] \
    [--ansible-sudo] \
    [--ansible-sudo-user <username>]
```

The following fixtures are available:


### ``ansible_module``

The ``ansible_module`` fixture allows tests and fixtures the ability to call
ansible [modules](http://docs.ansible.com/modules.html).  The fixture returns
JSON data describing the ansible module result.  The format of the JSON data
depends on the ``--ansible-inventory`` used, and the module.

For example, the ansible ``ping`` module

```python
@pytest.mark.ansible()
def test_ping(ansible_module):
    result = ansible_module.ping()
    assert 'ping' in result
```

A more involved example of updating the sshd configuration, and restarting the
service.

```python
def test_sshd_config(ansible_module):

    # increate sshd MaxSessions
    result = ansible_module.lineinfile(
        dest="/etc/ssh/sshd_config",
        regexp="^#?MaxSessions .*",
        line="MaxSessions 150")
    )

    # restart sshd
    result = ansible_module.service(
        name="sshd",
        state="restarted"
    )

    # do other stuff ...
```

###  ``ansible_facts``

The ``ansible_facts`` fixture returns a JSON structure representing the system
facts for the associated inventory.  Sample fact data is available in the
[ansible
documentation](http://docs.ansible.com/playbooks_variables.html#information-discovered-from-systems-facts).

Note, this fixture is provided for convenience and could easily be called using
``ansible_module.setup()``
