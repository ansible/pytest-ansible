import pytest


positive_host_patterns = {
    'all': 2,
    '*': 2,
    'localhost': 1,
    'local*': 1,
    'local*:&*host': 1,
    '!localhost': 1,
    'all[0]': 1,
    'all[-1]': 1,
    '*[0:1]': 2,  # this is confusing, but how host slicing works
    '*[0:]': 2,
}
negative_host_patterns = {
    'none': 0,
    'all[8:]': 0,
}


@pytest.mark.parametrize("host_pattern", positive_host_patterns.items(), ids=positive_host_patterns.keys())
def test_len(host_pattern, hosts):
    (pattern, expected_len) = host_pattern
    assert len(getattr(hosts, pattern)) == expected_len, "%s != %s" % (len(getattr(hosts, pattern)), expected_len)


@pytest.mark.parametrize("host_pattern", positive_host_patterns)
def test_contains(host_pattern, hosts):
    assert host_pattern in hosts.all
    assert host_pattern in hosts['all']


@pytest.mark.parametrize("host_pattern", negative_host_patterns)
def test_not_contains(host_pattern, hosts):
    assert host_pattern not in hosts.all
    assert host_pattern not in hosts['all']


def test_ansible_module_error(hosts):
    '''Verify that AnsibleModuleError is raised when no such module exists.'''
    from ansible.errors import AnsibleModuleError
    with pytest.raises(AnsibleModuleError):
        # The following allows us to introspect the exception object
        try:
            hosts.all.a_module_that_most_certainly_does_not_exist()
        except AnsibleModuleError, e:
            assert e.message == "The module {0} was not found in configured module paths.".format("a_module_that_most_certainly_does_not_exist")
            raise
        else:
            pytest.fail("ansible.errors.AnsibleModuleError was not raised as expected")
