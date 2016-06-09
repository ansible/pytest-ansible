import pytest
import ansible.errors

# class AdHocResult(object):
#
#     '''Pass.'''
#
#     def __init__(self, **kwargs):
#         self.__dict__.update(kwargs)
#
#         required_kwargs = ('contacted',)
#         for kwarg in required_kwargs:
#             assert kwarg in kwargs, "Missing required keyword argument '%s'" % kwarg
#             setattr(self, kwarg, kwargs.get(kwarg))
#
#     def __getitem__(self, item):
#         if item in self.__dict__:
#             return self.__dict__[item]
#         else:
#             if item in self.contacted:
#                 return ModuleResult(**self.contacted[item])
#             else:
#                 raise KeyError(item)
#
#     def __getattr__(self, attr):
#         """Maps values to attributes.
#         Only called if there *isn't* an attribute with this name
#         """
#         # if attr in self.__dict__:
#         #     return self.__dict__[attr]
#         # else:
#         if attr in self.contacted:
#             return ModuleResult(**self.contacted[attr])
#         else:
#             raise AttributeError("type AdHocResult has no attribute '%s'" % attr)
#
#     def __len__(self):
#         return len(self.contacted)
#
#     def __contains__(self, item):
#         return item in self.contacted
#
#     def keys(self):
#         return self.contacted.keys()
#
#     def items(self):
#         for k in self.contacted.keys():
#             yield (k, getattr(self, k))
#
#     def values(self):
#         for k in self.contacted.keys():
#             yield getattr(self, k)


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

valid_hosts = ('localhost', 'another_host')
invalid_hosts = ('none',)


def test_keys(hosts):
    result = hosts.all.ping()
    sorted_keys = result.keys()
    sorted_keys.sort()
    assert sorted_keys == ['another_host', 'localhost']


@pytest.mark.parametrize("host", valid_hosts)
def test_contains(hosts, host):
    result = hosts.all.ping()
    assert host in result


@pytest.mark.parametrize("host", invalid_hosts)
def test_not_contains(hosts, host):
    result = hosts.all.ping()
    assert host not in result


def Foo(hosts):
    # Test AdHocResult.__getitem__
    result = hosts.all.ping()
    assert result['localhost']
    for valid in valid_hosts:
        assert result[valid]
    for invalid in invalid_hosts:
        with pytest.raises(KeyError):
            assert result[invalid]

    # Test AdHocResult.__getattr__
    assert hasattr(result, 'localhost')
    for valid in valid_hosts:
        assert hasattr(result, valid)
    for invalid in invalid_hosts:
        assert not hasattr(result, invalid)
        with pytest.raises(AttributeError):
            getattr(result, invalid)

    # Test AdHocResult.__len__
    assert len(result) == 2

    # Test AdHocResult.keys
    sorted_keys = result.keys()
    sorted_keys.sort()
    assert sorted_keys == ['another_host', 'localhost']

    # Test ModuleResult.is_* properties
    result = hosts.localhost.debug(msg="testing")
    assert not result.localhost.is_changed
    assert not result.localhost.is_failed
    assert not result.localhost.is_skipped

    # Test ModuleResult.is_failed
    result = hosts.localhost.fail()
    assert not result.localhost.is_changed, result.localhost
    assert result.localhost.is_failed, result.localhost
    assert not result.localhost.is_skipped, result.localhost

    # Test ModuleResult.is_changed
    result = hosts.localhost.command('date')
    assert result.localhost.is_changed
    assert not result.localhost.is_failed
    assert not result.localhost.is_skipped

    # Test ModuleResult.values
    for host in result.values():
        assert host.is_changed
        assert not host.is_failed
        assert not host.is_skipped
