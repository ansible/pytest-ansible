"""Test the host manager."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import ansible.errors
import pytest

from pytest_ansible.host_manager.base import BaseHostManager
from pytest_ansible.host_manager.utils import get_host_manager

from .conftest import (
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
    assert len(_hosts[host_slice]) == num_hosts[include_extra_inventory], (
        f"{len(_hosts[host_slice])} != {num_hosts} for {host_slice}"
    )


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


def test_get_host_manager_unsupported() -> None:
    """get_host_manager raises when ansible < 2.13."""
    with (
        patch("pytest_ansible.host_manager.utils.has_ansible_v213", new=False),
        pytest.raises(RuntimeError, match="Unable to find any supported HostManager"),
    ):
        get_host_manager(inventory="localhost,")


def test_base_host_manager_default_dispatcher() -> None:
    """_default_dispatcher is a no-op."""
    manager = BaseHostManager.__new__(BaseHostManager)
    manager.options = {"inventory": "localhost,"}
    assert manager._default_dispatcher() is None


def test_base_host_manager_missing_required_kwargs() -> None:
    """check_required_kwargs raises TypeError when inventory is missing."""
    manager = BaseHostManager.__new__(BaseHostManager)
    manager.options = {}
    with pytest.raises(TypeError, match="Missing required keyword argument"):
        manager.check_required_kwargs()


def test_base_host_manager_has_matching_inventory_ansible_error() -> None:
    """has_matching_inventory returns False on AnsibleError."""
    manager = BaseHostManager.__new__(BaseHostManager)
    inv = MagicMock()
    inv.list_hosts.side_effect = ansible.errors.AnsibleError("bad pattern")
    manager.options = {"inventory_manager": inv}
    assert manager.has_matching_inventory("broken[") is False


def test_base_host_manager_getitem_from_dict() -> None:
    """__getitem__ returns values already present on the instance dict."""
    manager = BaseHostManager.__new__(BaseHostManager)
    manager.options = {"inventory": "localhost,"}
    manager.custom_attr = "value"  # type: ignore[attr-defined]
    assert manager["custom_attr"] == "value"


def test_base_host_manager_iter() -> None:
    """__iter__ yields dispatcher entries for matched hosts."""
    manager = BaseHostManager.__new__(BaseHostManager)
    host = MagicMock()
    host.name = "localhost"
    inv = MagicMock()
    inv.list_hosts.return_value = [host]
    dispatcher = MagicMock(return_value="disp")
    manager.options = {
        "inventory": "localhost,",
        "inventory_manager": inv,
        "host_pattern": "all",
    }
    manager._dispatcher = dispatcher
    manager.get_extra_inventory_hosts = MagicMock(return_value=[])  # type: ignore[method-assign]
    manager.has_matching_inventory = MagicMock(return_value=True)  # type: ignore[method-assign]

    result = list(iter(manager))
    assert result == ["disp"]


def test_base_host_manager_initialize_inventory_not_implemented() -> None:
    """initialize_inventory must be implemented by subclasses."""
    manager = BaseHostManager.__new__(BaseHostManager)
    with pytest.raises(NotImplementedError, match="Must be implemented by sub-class"):
        manager.initialize_inventory()
