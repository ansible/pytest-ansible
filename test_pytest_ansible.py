import pytest
import pytest_ansible
import json


# pytest_plugins = ['pytester', 'pytest_ansible']
pytest_plugins = 'pytester'


def test_module_ping_no_limit(ansible_module):
    '''Verify the ansible ping module across all inventory
    '''
    result = ansible_module.ping()
    print json.dumps(result, indent=2)
    assert len(result) == 5
    for host in result.values():
        assert 'failed' not in host
        assert 'invocation' in host
        assert 'module_name' in host['invocation']
        assert 'ping' == host['invocation']['module_name']

@pytest.mark.ansible(inventory='local,')
def test_module_ping_with_local_inventory(ansible_module):
    '''Verify the ansible ping module while specifying a inventory:local,
    '''
    result = ansible_module.ping()
    print json.dumps(result, indent=2)
    assert len(result) == 1
    for host in result.values():
        assert 'failed' not in host
        assert 'invocation' in host
        assert 'module_name' in host['invocation']
        assert 'ping' == host['invocation']['module_name']

@pytest.mark.ansible(host_pattern='all')
def test_module_ping_with_limit_all(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:all
    '''
    result = ansible_module.ping()
    print json.dumps(result, indent=2)
    assert len(result) == 5
    for host in result.values():
        assert 'failed' not in host
        assert 'invocation' in host
        assert 'module_name' in host['invocation']
        assert 'ping' == host['invocation']['module_name']

@pytest.mark.ansible(host_pattern='localhost')
def test_module_ping_limit_one(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:localhost
    '''
    result = ansible_module.ping()
    print json.dumps(result, indent=2)
    assert len(result) == 1
    for host in result.values():
        assert 'failed' not in host
        assert 'invocation' in host
        assert 'module_name' in host['invocation']
        assert 'ping' == host['invocation']['module_name']

@pytest.mark.ansible(host_pattern='localhost', sudo=True)
def test_module_ping_limit_one_with_sudo(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:localhost and sudo:true
    '''
    result = ansible_module.ping()
    print json.dumps(result, indent=2)
    assert len(result) == 1
    for host in result.values():
        assert 'failed' in host, \
            "Expecting a host failure when attempting to sudo to localhost " \
            "with connection_local"

@pytest.mark.ansible(host_pattern='random_limit_that_has_no_matches')
def test_module_ping_limit_no_matching_host(ansible_module):
    '''Verify the ansible ping fails when specifying a host_pattern that does not match
    '''
    with pytest.raises(pytest_ansible.AnsibleNoHostsMatch):
        ansible_module.ping()

def test_ansible_facts(ansible_facts):
    '''Verify that the ansible_facts fixture behaves as expected
    '''
    print json.dumps(ansible_facts, indent=2)
    assert len(ansible_facts) == 5
    for facts in ansible_facts.values():
        assert 'ansible_facts' in facts
        assert 'ansible_os_family' in facts['ansible_facts']
        assert 'ansible_distribution' in facts['ansible_facts']
