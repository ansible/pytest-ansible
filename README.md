# pytest-ansible

[![Build Status](https://img.shields.io/travis/com/ansible/pytest-ansible.svg)](https://travis-ci.com/ansible/pytest-ansible)
[![Coverage Status](https://coveralls.io/repos/github/ansible/pytest-ansible/badge.svg?branch=master)](https://coveralls.io/github/ansible/pytest-ansible?branch=master)
[![Requirements Status](https://requires.io/github/ansible/pytest-ansible/requirements.svg?branch=master)](https://requires.io/github/ansible/pytest-ansible/requirements/?branch=master)
[![Version](https://img.shields.io/pypi/v/pytest-ansible.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![License](https://img.shields.io/pypi/l/pytest-ansible.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/pytest-ansible.svg)](https://pypi.python.org/pypi/pytest-ansible/)


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
    [--inventory <path_to_inventory>] \
    [--host-pattern <host-pattern>] \
    [--connection <plugin>] \
    [--module-path <path_to_modules] \
    [--user <username>] \
    [--become] \
    [--become-user <username>] \
    [--become-method <method>] \
    [--limit <limit>] \
    [--check]
```

## Inventory

Using ansible first starts with defining your inventory.  This can be done
several ways, but to start, we'll use the ``ansible_adhoc`` fixture.

```python
def test_my_inventory(ansible_adhoc):
    hosts = ansible_adhoc()
```

In the example above, the `hosts` variable is an instance of the `HostManager`
class and describes your ansible inventory.  For this to work, you'll need to
tell `ansible` where to find your inventory.  Inventory can be anything
supported by ansible, which includes an [INI
file](http://docs.ansible.com/ansible/latest/intro_inventory.html) or an
executable script that returns [properly formatted
JSON](http://docs.ansible.com/ansible/latest/intro_dynamic_inventory.html).
For example, 

```bash
py.test --inventory my_inventory.ini --host-pattern all
```

or 

```bash
py.test --inventory path/to/my/script.py --host-pattern webservers
```
or 

```bash
py.test --inventory one.example.com,two.example.com --host-pattern all
```

In the above examples, the inventory provided at runtime will be used in all
tests that use the `ansible_adhoc` fixture.  A more realistic scenario may
involve using different inventory files (or host patterns) with different
tests.  To accomplish this, the fixture `ansible_adhoc` allows you to customize
the inventory parameters.  Read on for more detail on using the `ansible_adhoc`
fixture.

### Fixture ``ansible_adhoc``

The `ansible_adhoc` fixture returns a function used to initialize
a `HostManager` object.  The `ansible_adhoc` fixture will default to parameters
supplied to the `py.test` command-line, but also allows one to provide keyword
arguments used to initialize the inventory.

The example below demonstrates basic usage with options supplied at run-time to
`py.test`.

```python
def test_all_the_pings(ansible_adhoc):
    ansible_adhoc().all.ping()
```

The following example demonstrates available keyword arguments when creating
a `HostManager` object.

```python
def test_uptime(ansible_adhoc):
    # take down the database
    ansible_adhoc(inventory='db1.example.com,', user='ec2-user', 
        become=True, become_user='root').all.command('reboot')
```

The `HostManager` object returned by the `ansible_adhoc()` function provides
numerous ways of calling ansible modules against some, or all, of the
inventory.  The following demonstates sample usage.

```python
def test_host_manager(ansible_adhoc):
    hosts = ansible_adhoc()

    # __getitem__
    hosts['all'].ping()
    hosts['localhost'].ping()

    # __getattr__
    hosts.all.ping()
    hosts.localhost.ping()

    # Supports [ansible host patterns](http://docs.ansible.com/ansible/latest/intro_patterns.html)
    hosts['webservers:!phoenix'].ping()  # all webservers that are not in phoenix
    hosts[0].ping()
    hosts[0:2].ping()

    assert 'one.example.com' in hosts

    assert hasattr(hosts, 'two.example.com')

    for a_host in hosts:
        a_host.ping()
```

### Fixture ``localhost``

The `localhost` fixture is a convenience fixture that surfaces
a `ModuleDispatcher` instance for ansible host running `pytest`.  This is
convenient when using ansible modules that typically run on the local machine,
such as cloud modules (ec2, gce etc...).

```python
def test_do_something_cloudy(localhost, ansible_adhoc):
    """Deploy an ec2 instance using multiple fixtures."""
    params = dict(
        key_name='somekey',
        instance_type='t2.micro',
        image='ami-123456',
        wait=True,
        group='webserver',
        count=1,
        vpc_subnet_id='subnet-29e63245',
        assign_public_ip=True,
    )

    # Deploy an ec2 instance from localhost using the `ansible_adhoc` fixture
    ansible_adhoc(inventory='localhost,', connection='local').localhost.ec2(**params)

    # Deploy an ec2 instance from localhost using the `localhost` fixture
    localhost.ec2(**params)
```

### Fixture ``ansible_module``

The ``ansible_module`` fixture allows tests and fixtures to call [ansible
modules](http://docs.ansible.com/modules.html).  Unlike the `ansible_adhoc`
fixture, this fixture only uses the options supplied to `py.test` at run time.

A very basic example demonstrating the ansible [``ping`` module](http://docs.ansible.com/ping_module.html):

```python
def test_ping(ansible_module):
    ansible_module.ping()
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
    for facts in ansible_facts:
        if 'ec2.internal' != facts['ansible_domain']:
            pytest.skip("This test only applies to ec2 instances")

```

Additionally, since facts are just ansible modules, you could inspect the
contents of the ``ec2_facts`` module for greater granularity ...

```python

def test_terminate_us_east_1_instances(ansible_adhoc):

    for facts in ansible_adhoc().all.ec2_facts():
        if facts['ansible_ec2_placement_region'].startswith('us-east'):
            '''do some testing'''
```

### Parameterizing with ``pytest.mark.ansible``

Perhaps the ``--ansible-inventory=<inventory>`` includes many systems, but you
only wish to interact with a subset.  The ``pytest.mark.ansible`` marker can be
used to modify the ``pytest-ansible`` command-line parameters for a single
test.  Please note, the fixture `ansible_adhoc` is the prefer mechanism for
interacting with ansible inventory within tests.

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

### Inspecting results

When using the `ansible_adhoc`, `localhost` or `ansible_module` fixtures, the
object returned will be an instance of class ``AdHocResult``.  The
``AdHocResult`` class can be inspected as follows:

```python

def test_adhoc_result(ansible_adhoc):
    contacted = ansible_adhoc(inventory=my_inventory).command("date")

    # As a dictionary
    for (host, result) in contacted.items():
        assert result.is_successful, "Failed on host %s" % host
    for result in contacted.values():
        assert result.is_successful
    for host in contacted.keys():
        assert host in ['localhost', 'one.example.com']

    assert contacted.localhost.is_successful

    # As a list
    assert len(contacted) > 0
    assert 'localhost' in contacted

    # As an iterator
    for result in contacted:
        assert result.is_successful

    # With __getattr__
    assert contacted.localhost.is_successful

    # Or __gettem__
    assert contacted['localhost'].is_successful
```

Using the ``AdHocResult`` object provides ways to conveniently access results
for different hosts involved in the ansible adhoc command. Once the specific
host result is found, you may inspect the result of the ansible adhoc command
on that use by way of the ``ModuleResult`` interface.  The ``ModuleResult``
class represents the dictionary returned by the ansible module for a particular
host.  The contents of the dictionary depend on the module called.

The ``ModuleResult`` interface provides some convenient proprerties to
determine the success of the module call.  Examples are included below.

```python

def test_module_result(localhost):
    contacted = localhost.command("find /tmp")

    assert contacted.localhost.is_successful
    assert contacted.localhost.is_ok
    assert contacted.localhost.is_changed
    assert not contacted.localhost.is_failed

    contacted = localhost.shell("exit 1")
    assert contacted.localhost.is_failed
    assert not contacted.localhost.is_successful
```

The contents of the JSON returned by an ansible module differs from module to
module.  For guidance, consult the documentation and examples for the specific
[ansible module](http://docs.ansible.com/modules_by_category.html).

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

