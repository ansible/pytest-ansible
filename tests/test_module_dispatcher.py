import pytest  # noqa: INP001, D100

from conftest import NEGATIVE_HOST_PATTERNS, POSITIVE_HOST_PATTERNS


def test_type_error() -> None:
    """Verify that BaseModuleDispatcher cannot be instantiated."""
    from pytest_ansible.module_dispatcher import BaseModuleDispatcher

    with pytest.raises(TypeError, match="^Can't instantiate.*$"):
        BaseModuleDispatcher(inventory="localhost,")  # type: ignore[abstract] #pylint: disable=abstract-class-instantiated


@pytest.mark.requires_ansible_v2()
def test_importerror_requires_v1():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    with pytest.raises(ImportError):
        # pylint: disable=unused-import
        import pytest_ansible.module_dispatcher.v1  # type: ignore[import-not-found] # noqa: F401 # pylint: disable=import-error, no-name-in-module


@pytest.mark.parametrize(
    ("host_pattern", "num_hosts"),
    POSITIVE_HOST_PATTERNS,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_dispatcher_len(host_pattern, num_hosts, hosts, include_extra_inventory):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
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
def test_dispatcher_contains(host_pattern, num_hosts, hosts, include_extra_inventory):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert host_pattern in hosts["all"]


@pytest.mark.parametrize(("host_pattern", "num_hosts"), NEGATIVE_HOST_PATTERNS)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_dispatcher_not_contains(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    host_pattern,  # noqa: ANN001
    num_hosts,  # noqa: ANN001, ARG001
    hosts,  # noqa: ANN001
    include_extra_inventory,  # noqa: ANN001
):
    hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert host_pattern not in hosts["all"]


def test_ansible_module_error(hosts):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Verify that AnsibleModuleError is raised when no such module exists."""
    from pytest_ansible.errors import AnsibleModuleError

    with pytest.raises(AnsibleModuleError) as exc_info:
        hosts().all.a_module_that_most_certainly_does_not_exist()
    assert (
        str(exc_info.value)
        == f"The module {'a_module_that_most_certainly_does_not_exist'} was not found in configured module paths."  # noqa: E501
    )
