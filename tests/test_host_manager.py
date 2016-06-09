import pytest

pytestmark = [
    pytest.mark.unit,
]

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


def test_len(hosts):
    assert len(hosts) == 2


def test_keys(hosts):
    sorted_keys = hosts.keys()
    sorted_keys.sort()
    assert sorted_keys == ['another_host', 'localhost']


@pytest.mark.parametrize("host_pattern", positive_host_patterns)
def test_contains(host_pattern, hosts):
    assert host_pattern in hosts


@pytest.mark.parametrize("host_pattern", negative_host_patterns)
def test_not_contains(host_pattern, hosts):
    assert host_pattern not in hosts


@pytest.mark.parametrize("host_pattern", positive_host_patterns)
def test_getitem(host_pattern, hosts):
    assert hosts[host_pattern]


@pytest.mark.parametrize("host_pattern", negative_host_patterns)
def test_not_getitem(host_pattern, hosts):
    with pytest.raises(KeyError):
        assert hosts[host_pattern]


@pytest.mark.parametrize("host_pattern", positive_host_patterns)
def test_getattr(host_pattern, hosts):
    assert hasattr(hosts, host_pattern)


@pytest.mark.parametrize("host_pattern", negative_host_patterns)
def test_not_getattr(host_pattern, hosts):
    assert not hasattr(hosts, host_pattern)
    with pytest.raises(AttributeError):
        getattr(hosts, host_pattern)
