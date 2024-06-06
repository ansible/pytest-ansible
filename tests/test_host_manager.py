import pytest  # noqa: INP001, D100

from conftest import (
    ALL_EXTRA_HOSTS,
    ALL_HOSTS,
    EXTRA_HOST_POSITIVE_PATTERNS,
    NEGATIVE_HOST_PATTERNS,
    NEGATIVE_HOST_SLICES,
    POSITIVE_HOST_PATTERNS,
    POSITIVE_HOST_SLICES,
)


pytestmark = [
    pytest.mark.unit,
]


@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_host_manager_len(hosts, include_extra_inventory):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    _hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert len(_hosts) == len(ALL_HOSTS) + len(
        ALL_EXTRA_HOSTS if include_extra_inventory else [],
    )


@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_host_manager_keys(hosts, include_extra_inventory):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    _hosts = hosts(include_extra_inventory=include_extra_inventory)
    sorted_keys = _hosts.keys()
    sorted_keys.sort()
    for key in sorted_keys:
        assert key in ALL_HOSTS + (ALL_EXTRA_HOSTS if include_extra_inventory else [])


@pytest.mark.parametrize(
    ("host_pattern", "num_hosts"),
    POSITIVE_HOST_PATTERNS + EXTRA_HOST_POSITIVE_PATTERNS,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_host_manager_contains(host_pattern, num_hosts, hosts, include_extra_inventory):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    _hosts = hosts(include_extra_inventory=include_extra_inventory)
    if not include_extra_inventory and host_pattern.startswith("extra"):
        assert host_pattern not in _hosts, f"{host_pattern} in hosts"
    else:
        assert host_pattern in _hosts, f"{host_pattern} not in hosts"


@pytest.mark.parametrize(
    ("host_pattern", "num_hosts"),
    NEGATIVE_HOST_PATTERNS,
)
@pytest.mark.parametrize("include_extra_inventory", (True, False))
def test_host_manager_not_contains(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    host_pattern,  # noqa: ANN001
    num_hosts,  # noqa: ANN001, ARG001
    hosts,  # noqa: ANN001
    include_extra_inventory,  # noqa: ANN001
):
    _hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert host_pattern not in _hosts


@pytest.mark.parametrize(
    ("host_pattern", "num_hosts"),
    POSITIVE_HOST_PATTERNS + EXTRA_HOST_POSITIVE_PATTERNS,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_host_manager_getitem(host_pattern, num_hosts, hosts, include_extra_inventory):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    _hosts = hosts(include_extra_inventory=include_extra_inventory)
    if not include_extra_inventory and host_pattern.startswith("extra"):
        assert host_pattern not in _hosts
    else:
        assert _hosts[host_pattern]


@pytest.mark.parametrize(
    ("host_pattern", "num_hosts"),
    NEGATIVE_HOST_PATTERNS,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_host_manager_not_getitem(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    host_pattern,  # noqa: ANN001
    num_hosts,  # noqa: ANN001, ARG001
    hosts,  # noqa: ANN001
    include_extra_inventory,  # noqa: ANN001
):
    _hosts = hosts(include_extra_inventory=include_extra_inventory)
    with pytest.raises(KeyError):
        assert _hosts[host_pattern]


@pytest.mark.parametrize(
    ("host_pattern", "num_hosts"),
    POSITIVE_HOST_PATTERNS + EXTRA_HOST_POSITIVE_PATTERNS,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_host_manager_getattr(host_pattern, num_hosts, hosts, include_extra_inventory):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    _hosts = hosts(include_extra_inventory=include_extra_inventory)
    if not include_extra_inventory and host_pattern.startswith("extra"):
        assert not hasattr(_hosts, host_pattern)
    else:
        assert hasattr(_hosts, host_pattern)


@pytest.mark.parametrize(
    ("host_slice", "num_hosts"),
    POSITIVE_HOST_SLICES,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_host_manager_slice(host_slice, num_hosts, hosts, include_extra_inventory):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    _hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert (
        len(_hosts[host_slice]) == num_hosts[include_extra_inventory]
    ), f"{len(_hosts[host_slice])} != {num_hosts} for {host_slice}"


# pylint: disable=pointless-statement
@pytest.mark.parametrize(
    "host_slice",
    NEGATIVE_HOST_SLICES,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_host_manager_not_slice(host_slice, hosts, include_extra_inventory):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    _hosts = hosts(include_extra_inventory=include_extra_inventory)
    with pytest.raises(KeyError):
        _hosts[host_slice]


@pytest.mark.parametrize(
    ("host_pattern", "num_hosts"),
    NEGATIVE_HOST_PATTERNS,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_host_manager_not_getattr(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    host_pattern,  # noqa: ANN001
    num_hosts,  # noqa: ANN001, ARG001
    hosts,  # noqa: ANN001
    include_extra_inventory,  # noqa: ANN001
):
    _hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert not hasattr(_hosts, host_pattern)
    with pytest.raises(AttributeError):
        getattr(_hosts, host_pattern)


def test_defaults(request):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    from ansible.constants import DEFAULT_TRANSPORT  # pylint: disable=no-name-in-module

    plugin = request.config.pluginmanager.getplugin("ansible")
    hosts = plugin.initialize(config=request.config, request=request)

    assert "connection" in hosts.options
    assert hosts.options["connection"] == DEFAULT_TRANSPORT
