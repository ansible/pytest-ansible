# pytest-ansible

[![Current Version](https://pypip.in/v/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Supported Python versions](https://pypip.in/py_versions/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Downloads](https://pypip.in/d/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Build Status](https://travis-ci.org/jlaska/pytest-ansible.svg?branch=master)](https://travis-ci.org/jlaska/pytest-ansible)

This repository contains a plugin for ``py.test`` which adds several fixtures
for running ``ansible`` modules, or inspecting ``ansible_facts``.  While one
can simply call out to ``ansible`` using the ``subprocess`` module, having to
parse stdout to determine the outcome of the operation is unpleasant and prone
to error.  With ``pytest-ansible``, modules return JSON data which you can
inspect and act on, much like with an ansible
[playbook](http://docs.ansible.com/playbooks.html).

## Installation

Install this plugin using ``pip``

```bash
    pip install pytest-ansible
```

## Usage

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


### Fixture ``ansible_module``

The ``ansible_module`` fixture allows tests and fixtures to call ansible
[modules](http://docs.ansible.com/modules.html).  The fixture returns JSON data
describing the ansible module result.  The format of the JSON data depends on
the ``--ansible-inventory`` used, and the module.

For example, the ansible ``ping`` module:

```python
def test_ping(ansible_module):
    result = ansible_module.ping()
    assert 'ping' in result
```

A more involved example of updating the sshd configuration, and restarting the
service.

```python
def test_sshd_config(ansible_module):

    # Update sshd MaxSessions
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

### Fixture ``ansible_facts``

The ``ansible_facts`` fixture returns a JSON structure representing the system
facts for the associated inventory.  Sample fact data is available in the
[ansible
documentation](http://docs.ansible.com/playbooks_variables.html#information-discovered-from-systems-facts).

Note, this fixture is provided for convenience and could easily be called using
``ansible_module.setup()``.

A systems facts can be useful when deciding whether to skip a test ...

```python
def test_something_with_amazon_ec2(ansible_facts):
    for (host, facts) in ansible_facts.items():
        if 'ec2.internal' != facts['ansible_domain']:
            pytest.skip("This test only applies to ec2 instances")

```

Alternatively, you could inspect ``ec2_facts`` for greater granularity ...

```python

def test_terminate_us_east_1_instances(ansible_module):

    for (host, ec2_facts) in ansible_module.ec2_facts().items():
        if ec2_facts['ansible_ec2_placement_region'].startswith('us-east'):
            '''do some testing'''
```

### Parameterizing with ``pytest.mark.ansible``

Perhaps the ``--ansible-inventory=<inventory>`` includes many systems, but you
only wish to interact with a subset.  The ``pytest.mark.ansible`` marker can be
used to modify the ``pytest-ansible`` command-line parameters for a single test.

For example, to interact with the local system, you would adjust the
``host_pattern`` and ``connection`` parameters.

```python
@pytest.mark.ansible(host_pattern='local,', connection='local')
def test_copy_local(ansible_module):

    # create a file with random data
    result = ansible_module.copy(
        dest='/etc/motd',
        content='PyTest is amazing!',
        owner='root',
        group='root',
        mode='0644',
    )

    # assert the file was copied to all hosts in the inventory
    assert all(contacted['changed'] \
        for contacted in result['contacted'].values())
```

### Parameterizing with class variables

```python
class TestWebservers(object):

    ansible_host_pattern = 'webservers' # --ansible-host-pattern webservers
    ansible_user = 'steve'              # --ansible-user steve
    ansible_sudo = True                 # --ansible-sudo
    ansible_sudo_user = 'httpd'         # --ansible-sudo-user httpd

    def test_httpd_running(self, ansible_module):
        # ensure httpd is running
        result = ansible_module.service(name='httpd', state='running')

        # the above ansible module will ensure things are running.  The
        # following is only meant to demonstrate inspecting the resulting JSON
        # object.
        assert all(contacted['state'] == 'started' \
            for contacted in result['contacted'].values())
```

### Exception handling

If ``ansible`` is unable to connect to any inventory, an exception will be raised.

```python
@pytest.mark.ansible(inventory='unreachable.example.com,')
def test_shutdown(ansible_module):

    # attempt to ping a host that is down (or doesn't exist)
    pytest.raises(pytest_ansible.AnsibleHostUnreachable):
        ansible_module.ping()
```

Sometimes, only a single host is down, and others will have properly returned
data.  The following demonstrates how to catch the exception, and inspect the
results.

```python
@pytest.mark.ansible(inventory='good:bad')
def test_inventory_unreachable(ansible_module):
    exc_info = pytest.raises(pytest_ansible.AnsibleHostUnreachable, ansible_module.ping)
    result = exc_info.value.result

    # inspect the JSON result...
    for contacted in result['contacted'].values():
        assert contacted['ping'] == 'pong'

    for dark in result['dark'].values():
        assert dark['failed'] == True
```
