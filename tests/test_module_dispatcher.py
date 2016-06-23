import pytest
from conftest import (POSITIVE_HOST_PATTERNS, NEGATIVE_HOST_PATTERNS)


@pytest.mark.parametrize("host_pattern, num_hosts", POSITIVE_HOST_PATTERNS)
def test_len(host_pattern, num_hosts, hosts):
    assert len(getattr(hosts, host_pattern)) == num_hosts


@pytest.mark.parametrize("host_pattern, num_hosts", POSITIVE_HOST_PATTERNS)
def test_contains(host_pattern, num_hosts, hosts):
    assert host_pattern in hosts.all
    assert host_pattern in hosts['all']


@pytest.mark.parametrize("host_pattern, num_hosts", NEGATIVE_HOST_PATTERNS)
def test_not_contains(host_pattern, num_hosts, hosts):
    assert host_pattern not in hosts.all
    assert host_pattern not in hosts['all']


def test_ansible_module_error(hosts):
    '''Verify that AnsibleModuleError is raised when no such module exists.'''
    from pytest_ansible.errors import AnsibleModuleError
    with pytest.raises(AnsibleModuleError):
        # The following allows us to introspect the exception object
        try:
            hosts.all.a_module_that_most_certainly_does_not_exist()
        except AnsibleModuleError, e:
            assert e.message == "The module {0} was not found in configured module paths.".format("a_module_that_most_certainly_does_not_exist")
            raise
        else:
            pytest.fail("ansible.errors.AnsibleModuleError was not raised as expected")
