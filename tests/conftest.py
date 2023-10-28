import pytest


try:
    from ansible.utils import context_objects as co
except ImportError:
    # if it does not exist because of old version of ansible, we don't need it
    co = None


pytest_plugins = ["pytester"]


ALL_HOSTS = ["another_host", "localhost", "yet_another_host"]

POSITIVE_HOST_PATTERNS = [
    pytest.param("all", 3, id="0"),
    pytest.param("*", 3, id="1"),
    pytest.param("localhost", 1, id="2"),
    pytest.param("local*", 1, id="3"),
    pytest.param("local*,&*host", 1, id="4"),
    pytest.param("!localhost", 2, id="5"),
    pytest.param("all[0]", 1, id="6"),
    pytest.param("all[-1]", 1, id="7"),
    pytest.param("*[0-1]", 2, marks=pytest.mark.requires_ansible_v2(), id="9"),
    pytest.param(
        "*[0:1]",
        2,
        marks=pytest.mark.requires_ansible_v2(),
        id="10",
    ),  # this is confusing, but how host slicing works on v2
    pytest.param("*[0:]", 3, marks=pytest.mark.requires_ansible_v2(), id="11"),
]

NEGATIVE_HOST_PATTERNS = [
    pytest.param("none", 0, id="0"),
    pytest.param("all[8:]", 0, id="1"),
]

POSITIVE_HOST_SLICES = [
    pytest.param(slice(0, 0), 1, id="0"),
    pytest.param(slice(0, 1), 2, marks=pytest.mark.requires_ansible_v2(), id="2"),
    pytest.param(slice(0, 2), 3, marks=pytest.mark.requires_ansible_v2(), id="4"),
    pytest.param(slice(0), 1, id="5"),
    pytest.param(slice(1), 1, id="6"),
    pytest.param(slice(2), 1, id="7"),
    pytest.param(slice(3), 1, id="8"),
]

NEGATIVE_HOST_SLICES = [
    slice(None),
    slice(-1),
]


def pytest_runtest_setup(item):
    # Conditionally skip tests that are pinned to a specific ansible version
    if isinstance(item, pytest.Function):
        # conditionally xfail
        mark = item.get_closest_marker("ansible_v2_xfail")
        if mark:
            item.add_marker(
                pytest.xfail(
                    reason="expected failure on >= ansible-2.*",
                    raises=mark.kwargs.get("raises"),
                ),
            )


# pylint: disable=too-few-public-methods
class PyTestOption:
    """Helper class that provides methods for creating and managing an inventory file."""

    def __init__(self, config, testdir) -> None:
        self.config = config

        # Create inventory file
        self.inventory = testdir.makefile(
            ".ini",
            inventory="""
            [local]

            [local:children]
            reachable

            [reachable]
            localhost ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.2 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.3 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.4 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.5 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'

            [unreachable]
            unreachable-host-1.example.com
            unreachable-host-2.example.com
            unreachable-host-3.example.com
        """,
        )

        # Create ansible.cfg file

    @property
    def args(self):
        args = []
        args.append("--tb")
        args.append("native")
        return args


@pytest.fixture(autouse=True)
def _clear_global_context():
    # Reset the stored command line args
    # if context object does not exist because of old version of ansible, we don't need it
    if co is not None:
        co.GlobalCLIArgs._Singleton__instance = None


@pytest.fixture()
def option(request, testdir):
    """Returns an instance of PyTestOption to help tests pass parameters and
    use a common inventory file.
    """
    return PyTestOption(request.config, testdir)


@pytest.fixture()
def hosts():
    from pytest_ansible.host_manager import get_host_manager

    return get_host_manager(inventory=",".join(ALL_HOSTS), connection="local")
