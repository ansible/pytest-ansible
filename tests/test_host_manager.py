import pytest
from ansible.errors import AnsibleError

pytestmark = [
    pytest.mark.unit,
]

positive_host_patterns = [
    ('all', 2),
    ('*', 2),
    ('localhost', 1),
    ('local*', 1),
    ('local*,&*host', 1),
    ('!localhost', 1),
    ('all[0]', 1),
    ('all[-1]', 1),
    ('*[0-1]', 2),
    pytest.mark.requires_ansible_v2(('*[0:1]', 2)),  # this is confusing, but how host slicing works on v2
    pytest.mark.requires_ansible_v2(('*[0:]', 2)),
]

negative_host_patterns = [
    ('none', 0),
    ('all[8:]', 0),
]


def test_len(hosts):
    assert len(hosts) == 2


def test_keys(hosts):
    sorted_keys = hosts.keys()
    sorted_keys.sort()
    assert sorted_keys == ['another_host', 'localhost']


@pytest.mark.parametrize("host_pattern, num_hosts", positive_host_patterns)
def test_contains(host_pattern, num_hosts, hosts):
    assert host_pattern in hosts, "{0} not in hosts".format(host_pattern)


@pytest.mark.parametrize("host_pattern, num_hosts", negative_host_patterns)
def test_not_contains(host_pattern, num_hosts, hosts):
    assert host_pattern not in hosts


@pytest.mark.parametrize("host_pattern, num_hosts", positive_host_patterns)
def test_getitem(host_pattern, num_hosts, hosts):
    assert hosts[host_pattern]


@pytest.mark.parametrize("host_pattern, num_hosts", negative_host_patterns)
def test_not_getitem(host_pattern, num_hosts, hosts):
    with pytest.raises(KeyError):
        assert hosts[host_pattern]


@pytest.mark.parametrize("host_pattern, num_hosts", positive_host_patterns)
def test_getattr(host_pattern, num_hosts, hosts):
    assert hasattr(hosts, host_pattern)


@pytest.mark.parametrize("host_pattern, num_hosts", negative_host_patterns)
def test_not_getattr(host_pattern, num_hosts, hosts):
    assert not hasattr(hosts, host_pattern)
    with pytest.raises(AttributeError):
        getattr(hosts, host_pattern)


# This should probably be made more generic for all options (and moved elsewhere)
@pytest.mark.ansible_v1_xfail(raises=AnsibleError)
def test_defaults(request):
    from ansible.constants import DEFAULT_TRANSPORT

    plugin = request.config.pluginmanager.getplugin("ansible")
    hosts = plugin.initialize(request)

    # from pytest_ansible.host_manager import get_host_manager
    # hosts = get_host_manager(inventory='unknown.example.com,')
    assert 'connection' in hosts.options
    assert hosts.options['connection'] == DEFAULT_TRANSPORT
