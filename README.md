# pytest-ansible

[![Current Version](https://pypip.in/v/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Supported Python versions](https://pypip.in/py_versions/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Downloads](https://pypip.in/d/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Build Status](https://travis-ci.org/jlaska/pytest-ansible.svg?branch=master)](https://travis-ci.org/jlaska/pytest-ansible)
[![Coverage Status](https://coveralls.io/repos/jlaska/pytest-ansible/badge.svg?branch=master)](https://coveralls.io/r/jlaska/pytest-ansible?branch=master)
[![License](https://pypip.in/license/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)

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
[modules](http://docs.ansible.com/modules.html).

A very basic example demonstrating the ansible [``ping`` module](http://docs.ansible.com/ping_module.html):

```python
def test_ping(ansible_module):
    ansible_module.ping()
```

The above example doesn't do any validation/inspection of the return value.  A
more likely use case will involve inspecting the return value.  The
``ansible_module`` fixture returns a JSON data describing the ansible module
result.  The format of the JSON data depends on the ``--ansible-inventory``
used, and the [ansible module](http://docs.ansible.com/modules_by_category.html).

The following example demonstrates inspecting the module result.

```python
def test_ping(ansible_module):
    contacted = ansible_module.ping()
    for (host, result) in contacted.items():
        assert 'ping' in result, \
            "Failure on host:%s" % host
        assert result['ping'] == 'pong', \
            "Unexpected ping response: %s" % result['ping']
```

A more involved example of updating the sshd configuration, and restarting the
service.

```python
def test_sshd_config(ansible_module):

    # update sshd MaxSessions
    contacted = ansible_module.lineinfile(
        dest="/etc/ssh/sshd_config",
        regexp="^#?MaxSessions .*",
        line="MaxSessions 150")
    )

    # assert desired outcome
    for (host, result) in contacted.items():
        assert 'failed' not in result, result['msg']
        assert 'changed' in result

    # restart sshd
    contacted = ansible_module.service(
        name="sshd",
        state="restarted"
    )

    # assert successful restart
    for (host, result) in contacted.items():
        assert 'changed' in result and result['changed']
        assert result['name'] == 'sshd'

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
    contacted = ansible_module.copy(
        dest='/etc/motd',
        content='PyTest is amazing!',
        owner='root',
        group='root',
        mode='0644',
    )

    # assert only a single host was contacted
    assert len(contacted) == 1, \
        "Unexpected number of hosts contacted (%d != %d)" % \
        (1, len(contacted))

    assert 'local' in contacted

    # assert the copy module reported changes
    assert 'changed' in contacted['local']
    assert contacted['local']['changed']
```

Note, the parameters provided by ``pytest.mark.ansible`` will apply to all
class methods.

```python
@pytest.mark.ansible(host_pattern='local,', connection='local')
class Test_Local(object):
    def test_install(self, ansible_module):
        '''do some testing'''
    def test_template(self, ansible_module):
        '''do some testing'''
    def test_service(self, ansible_module):
        '''do some testing'''
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

Sometimes, only a single host is unreachable, and others will have properly
returned data.  The following demonstrates how to catch the exception, and
inspect the results.

```python
@pytest.mark.ansible(inventory='good:bad')
def test_inventory_unreachable(ansible_module):
    exc_info = pytest.raises(pytest_ansible.AnsibleHostUnreachable, ansible_module.ping)
    (contacted, dark) = exc_info.value.results

    # inspect the JSON result...
    for (host, result) in contacted.items():
        assert result['ping'] == 'pong'

    for (host, result) in dark.items():
        assert result['failed'] == True
```

