import pytest
import pytest_ansible


# pytest_plugins = ['pytester', 'pytest_ansible']
pytest_plugins = 'pytester'


def assert_ping_response_success(data):
    return assert_ping_response(data, failed=False)


def assert_ping_response_failure(data):
    return assert_ping_response(data, failed=True)


def assert_ping_response(data, failed):

    if failed:
        assert 'failed' in data
        assert data['failed']
    else:
        assert 'failed' not in data
        assert 'invocation' in data
        assert 'module_name' in data['invocation']
        assert 'ping' == data['invocation']['module_name']


def test_module_ping_without_limit(ansible_module):
    '''Verify the ansible ping module across all inventory
    '''
    exc_info = pytest.raises(pytest_ansible.AnsibleHostUnreachable, ansible_module.ping)
    result = exc_info.value.result

    # assert contacted hosts ...
    assert 'contacted' in result
    assert len(result['contacted']) == len(ansible_module.inventory_manager.list_hosts('!unreachable'))
    for contacted in result['contacted'].values():
        assert_ping_response_success(contacted)

    # assert dark hosts ...
    assert 'dark' in result
    assert len(result['dark']) == len(ansible_module.inventory_manager.list_hosts('unreachable'))
    for dark in result['dark'].values():
        assert_ping_response_failure(dark)


@pytest.mark.ansible(host_pattern='localhost')
def test_module_ping_with_limit_host(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:localhost
    '''
    result = ansible_module.ping()

    # assert contacted hosts ...
    assert 'contacted' in result
    assert len(result['contacted']) == 1
    for contacted in result['contacted'].values():
        assert_ping_response_success(contacted)

    # assert dark hosts ...
    assert not result['dark']


@pytest.mark.ansible(host_pattern='unreachable')
def test_module_ping_with_limit_group(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:unreachable
    '''
    exc_info = pytest.raises(pytest_ansible.AnsibleHostUnreachable, ansible_module.ping)
    result = exc_info.value.result

    # assert no contacted hosts ...
    assert not result['contacted']

    # assert dark hosts ...
    assert result['dark']
    assert len(result['dark']) == len(ansible_module.inventory_manager.list_hosts('unreachable'))
    for dark in result['dark'].values():
        assert_ping_response_failure(dark)


@pytest.mark.ansible(host_pattern='!unreachable')
def test_module_ping_with_limit_not_group(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:!unreachable
    '''
    result = ansible_module.ping()

    # assert contacted hosts ...
    assert 'contacted' in result
    assert len(result['contacted']) == len(ansible_module.inventory_manager.list_hosts('!unreachable'))
    for contacted in result['contacted'].values():
        assert_ping_response_success(contacted)

    # assert no dark hosts ...
    assert not result['dark']


@pytest.mark.ansible(connection='local')
def test_module_ping_override_connection(ansible_module):
    '''Verify the ansible ping module while specifying a connection:local
    '''
    result = ansible_module.ping()

    # assert contacted hosts ...
    assert 'contacted' in result
    assert len(result['contacted']) == len(ansible_module.inventory_manager.list_hosts('all'))
    for contacted in result['contacted'].values():
        assert_ping_response_success(contacted)

    # assert no dark hosts ...
    assert not result['dark']


@pytest.mark.ansible(inventory='local,', connection='local')
def test_module_ping_override_inventory_and_connection(ansible_module):
    '''Verify the ansible ping module while specifying a inventory:local, and connection:local
    '''
    result = ansible_module.ping()

    # assert contacted hosts ...
    assert 'contacted' in result
    assert len(result['contacted']) == 1
    for contacted in result['contacted'].values():
        assert_ping_response_success(contacted)

    # assert no dark hosts ...
    assert not result['dark']


@pytest.mark.ansible(host_pattern='localhost', sudo=True)
def test_module_ping_with_limit_and_sudo(ansible_module):
    '''Verify the ansible ping module while specifying a host_pattern:localhost and sudo:true
    '''
    result = ansible_module.ping()

    # assert contacted hosts ...
    assert 'contacted' in result
    assert len(result['contacted']) == 1
    for contacted in result['contacted'].values():
        assert_ping_response_failure(contacted)

    # assert no dark hosts ...
    assert not result['dark']


@pytest.mark.ansible(host_pattern='random_limit_that_has_no_matches')
def test_module_ping_with_limit_no_matching_host(ansible_module):
    '''Verify the ansible ping fails when specifying a host_pattern that does not match
    '''
    with pytest.raises(pytest_ansible.AnsibleNoHostsMatch):
        ansible_module.ping()


def test_ansible_facts(ansible_facts, ansible_module):
    '''Verify that the ansible_facts fixture behaves as expected
    '''
    result = ansible_facts

    # assert contacted hosts ...
    assert 'contacted' in result
    assert len(result['contacted']) == len(ansible_module.inventory_manager.list_hosts('!unreachable'))
    for host_facts in result['contacted'].values():
        assert 'ansible_facts' in host_facts
        assert 'ansible_os_family' in host_facts['ansible_facts']
        assert 'ansible_distribution' in host_facts['ansible_facts']

    # assert dark hosts ...
    assert 'dark' in result
    assert len(result['dark']) == len(ansible_module.inventory_manager.list_hosts('unreachable'))
    for dark in result['dark'].values():
        assert_ping_response_failure(dark)
