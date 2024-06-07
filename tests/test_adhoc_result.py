from types import GeneratorType  # noqa: INP001, D100

import pytest

from conftest import ALL_EXTRA_HOSTS, ALL_HOSTS

from pytest_ansible.results import ModuleResult


invalid_hosts = [
    pytest.param("none"),
    pytest.param("all"),
    pytest.param("*", id="glob"),
    pytest.param("local*", id="glob2"),
]


@pytest.fixture(params=[True, False], name="adhoc_result")
def fixture_adhoc_result(request, hosts):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    def create_hosts():  # type: ignore[no-untyped-def]  # noqa: ANN202
        _hosts = hosts(include_extra_inventory=request.param)
        return _hosts.all.ping(), request.param

    return create_hosts


def test_len(adhoc_result):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    adhoc_result_ret, include_extra_inv = adhoc_result()
    assert len(adhoc_result_ret) == len(ALL_HOSTS) + len(
        ALL_EXTRA_HOSTS if include_extra_inv else [],
    )


def test_keys(adhoc_result):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    adhoc_result_ret, include_extra_inv = adhoc_result()
    assert set(adhoc_result_ret) == set(
        ALL_HOSTS + (ALL_EXTRA_HOSTS if include_extra_inv else []),
    )


def test_items(adhoc_result):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    adhoc_result_ret, include_extra_inv = adhoc_result()
    items = adhoc_result_ret.items()
    assert isinstance(items, GeneratorType)
    count = 0
    for count, item in enumerate(items, 1):  # noqa: B007
        assert isinstance(item, tuple)
        assert isinstance(item[0], str)
        assert isinstance(item[1], ModuleResult)
    assert count == len(ALL_HOSTS + (ALL_EXTRA_HOSTS if include_extra_inv else []))


def test_values(adhoc_result):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    adhoc_result_ret, include_extra_inv = adhoc_result()
    values = adhoc_result_ret.values()
    assert isinstance(values, list)
    # assure that it is a copy
    assert values is not adhoc_result_ret.contacted.values()
    count = 0
    for count, val in enumerate(values, 1):  # noqa: B007
        assert isinstance(val, ModuleResult)
    assert count == len(ALL_HOSTS) + len(ALL_EXTRA_HOSTS if include_extra_inv else [])


@pytest.mark.parametrize("host", ALL_HOSTS + ALL_EXTRA_HOSTS)
def test_contains(adhoc_result, host):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    adhoc_result_ret, include_extra_inv = adhoc_result()
    if not include_extra_inv and host in ALL_EXTRA_HOSTS:
        assert host not in adhoc_result_ret
    else:
        assert host in adhoc_result_ret


@pytest.mark.parametrize("host", invalid_hosts)
def test_not_contains(adhoc_result, host):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    adhoc_result_ret, dummy = adhoc_result()
    assert host not in adhoc_result_ret


@pytest.mark.parametrize("host_pattern", ALL_HOSTS + ALL_EXTRA_HOSTS)
def test_getitem(adhoc_result, host_pattern):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    adhoc_result_ret, include_extra_inv = adhoc_result()
    if not include_extra_inv and host_pattern in ALL_EXTRA_HOSTS:
        with pytest.raises(KeyError):
            assert adhoc_result_ret[host_pattern]
    else:
        assert adhoc_result_ret[host_pattern]
        assert isinstance(adhoc_result_ret[host_pattern], ModuleResult)


@pytest.mark.parametrize("host_pattern", invalid_hosts)
def test_not_getitem(adhoc_result, host_pattern):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    adhoc_result_ret, dummy = adhoc_result()
    with pytest.raises(KeyError):
        assert adhoc_result_ret[host_pattern]


@pytest.mark.parametrize("host_pattern", ALL_HOSTS + ALL_EXTRA_HOSTS)
def test_getattr(adhoc_result, host_pattern):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    adhoc_result_ret, include_extra_inv = adhoc_result()
    if not include_extra_inv and host_pattern in ALL_EXTRA_HOSTS:
        assert not hasattr(adhoc_result_ret, host_pattern)
    else:
        assert hasattr(adhoc_result_ret, host_pattern)
        assert isinstance(adhoc_result_ret[host_pattern], ModuleResult)


@pytest.mark.parametrize("host_pattern", invalid_hosts)
def test_not_getattr(adhoc_result, host_pattern):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    adhoc_result_ret, dummy = adhoc_result()
    assert not hasattr(adhoc_result_ret, host_pattern)
    with pytest.raises(AttributeError):
        getattr(adhoc_result_ret, host_pattern)


@pytest.mark.requires_ansible_v2()
def test_connection_failure_v2():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    from pytest_ansible.errors import AnsibleConnectionFailure
    from pytest_ansible.host_manager.utils import get_host_manager

    hosts = get_host_manager(inventory="unknown.example.com,", connection="smart")
    with pytest.raises(AnsibleConnectionFailure) as exc_info:
        hosts.all.ping()
    # Assert message
    assert exc_info.value.message == "Host unreachable in the inventory"
    # Assert contacted
    assert exc_info.value.contacted == {}
    # Assert dark
    assert "unknown.example.com" in exc_info.value.dark
    # Assert unreachable
    assert "unreachable" in exc_info.value.dark["unknown.example.com"], exc_info.value.dark.keys()
    assert exc_info.value.dark["unknown.example.com"]["unreachable"]
    # Assert msg
    assert "msg" in exc_info.value.dark["unknown.example.com"]
    assert (
        "Failed to connect to the host via ssh" in exc_info.value.dark["unknown.example.com"]["msg"]
    )


@pytest.mark.requires_ansible_v2()
def test_connection_failure_extra_inventory_v2():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    from pytest_ansible.errors import AnsibleConnectionFailure
    from pytest_ansible.host_manager.utils import get_host_manager

    hosts = get_host_manager(
        inventory="localhost",
        extra_inventory="unknown.example.extra.com,",
    )
    with pytest.raises(AnsibleConnectionFailure) as exc_info:
        hosts.all.ping()
    # Assert message
    assert exc_info.value.message == "Host unreachable in the extra inventory"
    # Assert contacted
    assert exc_info.value.contacted == {}
    # Assert dark
    assert "unknown.example.extra.com" in exc_info.value.dark
    # Assert unreachable
    assert (
        "unreachable" in exc_info.value.dark["unknown.example.extra.com"]
    ), exc_info.value.dark.keys()
    assert exc_info.value.dark["unknown.example.extra.com"]["unreachable"]
    # Assert msg
    assert "msg" in exc_info.value.dark["unknown.example.extra.com"]
    assert (
        "Failed to connect to the host via ssh"
        in exc_info.value.dark["unknown.example.extra.com"]["msg"]
    )
