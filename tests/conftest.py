import pytest  # noqa: INP001, D100

from pytest_ansible.host_manager.utils import get_host_manager


try:
    from ansible.utils import context_objects as co
except ImportError:
    # if it does not exist because of old version of ansible, we don't need it
    co = None

pytest_plugins = ["pytester"]

ALL_HOSTS = ["another_host", "localhost", "yet_another_host"]

ALL_EXTRA_HOSTS = ["extra-hosts", "extra-hosts_extra", "yet_another_extra-hosts"]

POSITIVE_HOST_PATTERNS = [
    # True means we are including the extra inventory, False not
    pytest.param("all", {True: 6, False: 3}, id="0"),
    pytest.param("*", {True: 6, False: 3}, id="1"),
    pytest.param("localhost", {True: 2, False: 1}, id="2"),
    pytest.param("local*", {True: 1, False: 1}, id="3"),
    pytest.param("local*,&*host", {True: 1, False: 1}, id="4"),
    pytest.param("!localhost", {True: 5, False: 2}, id="5"),
    pytest.param("all[0]", {True: 2, False: 1}, id="6"),
    pytest.param("all[-1]", {True: 2, False: 1}, id="7"),
    pytest.param(
        "*[0:1]",
        {True: 4, False: 2},
        marks=pytest.mark.requires_ansible_v2(),
        id="8",
    ),
    # this is confusing, but how host slicing works on v2
    pytest.param(
        "*[0:]",
        {True: 6, False: 3},
        marks=pytest.mark.requires_ansible_v2(),
        id="9",
    ),
]

EXTRA_HOST_POSITIVE_PATTERNS = [
    # True means we are including the extra inventory, False not
    pytest.param(
        "extra-hosts",
        {True: 1, False: 0},
        marks=pytest.mark.requires_ansible_v2(),
        id="10",
    ),
    pytest.param(
        "extra-hosts_extra",
        {True: 1, False: 0},
        marks=pytest.mark.requires_ansible_v2(),
        id="11",
    ),
    pytest.param(
        "extra-host*",
        {True: 2, False: 0},
        marks=pytest.mark.requires_ansible_v2(),
        id="12",
    ),
]

NEGATIVE_HOST_PATTERNS = [
    # True means we are including the extra inventory, False not
    pytest.param("none", {True: 0, False: 0}, id="0"),
    pytest.param("all[8:]", {True: 0, False: 0}, id="1"),
]

POSITIVE_HOST_SLICES = [
    # True means we are including the extra inventory, False not
    pytest.param(slice(0, 0), {True: 2, False: 1}, id="0"),
    pytest.param(
        slice(0, 1),
        {True: 4, False: 2},
        marks=pytest.mark.requires_ansible_v2(),
        id="1",
    ),
    pytest.param(
        slice(0, 2),
        {True: 6, False: 3},
        marks=pytest.mark.requires_ansible_v2(),
        id="2",
    ),
    pytest.param(slice(0), {True: 2, False: 1}, id="3"),
    pytest.param(slice(1), {True: 2, False: 1}, id="4"),
    pytest.param(slice(2), {True: 2, False: 1}, id="5"),
    pytest.param(slice(3), {True: 2, False: 1}, id="6"),
]

NEGATIVE_HOST_SLICES = [
    slice(None),
    slice(-1),
]


def pytest_runtest_setup(item):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    # Conditionally skip tests that are pinned to a specific ansible version
    if isinstance(item, pytest.Function):
        # conditionally xfail
        mark = item.get_closest_marker("ansible_v2_xfail")
        if mark:
            item.add_marker(
                pytest.xfail(
                    reason="expected failure on >= ansible-2.*",
                ),
            )


class PyTestOption:
    """Helper class that provides methods for creating and managing an inventory file."""

    def __init__(self, config, pytester) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001, D107
        self.config = config

        # Create inventory file
        self.inventory = pytester.makefile(
            ".ini",
            inventory="""
            [local]

            [local:children]
            reachable

            [reachable]
            localhost ansible_connection=local
            127.0.0.2 ansible_connection=local
            127.0.0.3 ansible_connection=local
            127.0.0.4 ansible_connection=local
            127.0.0.5 ansible_connection=local

            [unreachable]
            unreachable-host-1.example.com
            unreachable-host-2.example.com
            unreachable-host-3.example.com
        """,
        )

        # Create ansible.cfg file

    @property
    def args(self):  # type: ignore[no-untyped-def]  # noqa: ANN201, D102
        return ["--tb", "native"]


@pytest.fixture(autouse=True)
def _clear_global_context():  # type: ignore[no-untyped-def]  # noqa: ANN202
    # Reset the stored command line args
    # if context object does not exist because of old version of ansible, we don't need it
    if co is not None:
        co.GlobalCLIArgs._Singleton__instance = None


@pytest.fixture()
def option(request, pytester):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Returns an instance of PyTestOption to help tests pass parameters and
    use a common inventory file.
    """  # noqa: D205
    return PyTestOption(request.config, pytester)


@pytest.fixture()
def hosts():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    def create_host_manager(include_extra_inventory=False):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN202, FBT002
        kwargs = {"inventory": ",".join(ALL_HOSTS), "connection": "local"}
        if include_extra_inventory:
            kwargs["extra_inventory"] = ",".join(ALL_EXTRA_HOSTS)
        return get_host_manager(**kwargs)

    return create_host_manager
