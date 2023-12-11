import pytest

from conftest import NEGATIVE_HOST_PATTERNS, POSITIVE_HOST_PATTERNS


def test_runtime_error():
    from pytest_ansible.module_dispatcher import BaseModuleDispatcher

    bmd = BaseModuleDispatcher(inventory="localhost,")
    with pytest.raises(RuntimeError):
        bmd.has_module("foo")

    with pytest.raises(RuntimeError):
        bmd._run("foo")


@pytest.mark.requires_ansible_v2()
def test_importerror_requires_v1():
    with pytest.raises(ImportError):
        # pylint: disable=unused-import
        import pytest_ansible.module_dispatcher.v1  # NOQA


@pytest.mark.parametrize(
    ("host_pattern", "num_hosts"),
    POSITIVE_HOST_PATTERNS,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_dispatcher_len(host_pattern, num_hosts, hosts, include_extra_inventory):
    hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert len(getattr(hosts, host_pattern)) == num_hosts[include_extra_inventory]


@pytest.mark.parametrize(
    ("host_pattern", "num_hosts"),
    POSITIVE_HOST_PATTERNS,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_dispatcher_contains(host_pattern, num_hosts, hosts, include_extra_inventory):
    hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert host_pattern in hosts["all"]


@pytest.mark.parametrize(("host_pattern", "num_hosts"), NEGATIVE_HOST_PATTERNS)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_dispatcher_not_contains(
    host_pattern,
    num_hosts,
    hosts,
    include_extra_inventory,
):
    hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert host_pattern not in hosts["all"]


def test_ansible_module_error(hosts):
    """Verify that AnsibleModuleError is raised when no such module exists."""
    from pytest_ansible.errors import AnsibleModuleError

    with pytest.raises(AnsibleModuleError) as exc_info:
        hosts().all.a_module_that_most_certainly_does_not_exist()
    assert (
        str(exc_info.value)
        == f"The module {'a_module_that_most_certainly_does_not_exist'} was not found in configured module paths."
    )
