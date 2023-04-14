import pytest
from conftest import NEGATIVE_HOST_PATTERNS, POSITIVE_HOST_PATTERNS


def test_runtime_error():
    from pytest_ansible.module_dispatcher import BaseModuleDispatcher

    bmd = BaseModuleDispatcher(inventory="localhost,")
    with pytest.raises(RuntimeError):
        bmd.has_module("foo")

    with pytest.raises(RuntimeError):
        bmd._run("foo")


# pylint: disable=unused-import
@pytest.mark.requires_ansible_v1()
def test_importerror_requires_v2():
    with pytest.raises(ImportError):
        import pytest_ansible.module_dispatcher.v2  # NOQA


@pytest.mark.requires_ansible_v2()
def test_importerror_requires_v1():
    with pytest.raises(ImportError):
        import pytest_ansible.module_dispatcher.v1  # NOQA


@pytest.mark.parametrize(("host_pattern", "num_hosts"), POSITIVE_HOST_PATTERNS)
def test_len(host_pattern, num_hosts, hosts):
    assert len(getattr(hosts, host_pattern)) == num_hosts


@pytest.mark.parametrize(("host_pattern", "num_hosts"), POSITIVE_HOST_PATTERNS)
def test_contains(host_pattern, num_hosts, hosts):
    assert host_pattern in hosts.all
    assert host_pattern in hosts["all"]


@pytest.mark.parametrize(("host_pattern", "num_hosts"), NEGATIVE_HOST_PATTERNS)
def test_not_contains(host_pattern, num_hosts, hosts):
    assert host_pattern not in hosts.all
    assert host_pattern not in hosts["all"]


def test_ansible_module_error(hosts):
    """Verify that AnsibleModuleError is raised when no such module exists."""
    from pytest_ansible.errors import AnsibleModuleError

    with pytest.raises(AnsibleModuleError) as exc_info:
        hosts.all.a_module_that_most_certainly_does_not_exist()
    assert (
        str(exc_info.value)
        == f"The module {'a_module_that_most_certainly_does_not_exist'} was not found in configured module paths."
    )
