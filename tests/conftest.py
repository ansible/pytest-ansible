import pytest
from pytest_ansible.has_version import has_ansible_v1, has_ansible_v24

try:
    from ansible.utils import context_objects as co
except ImportError:
    # if it does not exist because of old version of ansible, we don't need it
    co = None


pytest_plugins = ["pytester"]


ALL_HOSTS = ["another_host", "localhost", "yet_another_host"]

POSITIVE_HOST_PATTERNS = [
    ("all", 3),
    ("*", 3),
    ("localhost", 1),
    ("local*", 1),
    ("local*,&*host", 1),
    ("!localhost", 2),
    ("all[0]", 1),
    ("all[-1]", 1),
    pytest.param("*[0-1]", 1, marks=pytest.mark.requires_ansible_v1()),
    pytest.param("*[0-1]", 2, marks=pytest.mark.requires_ansible_v2()),
    pytest.param(
        "*[0:1]",
        2,
        marks=pytest.mark.requires_ansible_v2(),
    ),  # this is confusing, but how host slicing works on v2
    pytest.param("*[0:]", 3, marks=pytest.mark.requires_ansible_v2()),
]

NEGATIVE_HOST_PATTERNS = [
    ("none", 0),
    ("all[8:]", 0),
]

POSITIVE_HOST_SLICES = [
    (slice(0, 0), 1),
    pytest.param(slice(0, 1), 1, marks=pytest.mark.requires_ansible_v1()),
    pytest.param(slice(0, 1), 2, marks=pytest.mark.requires_ansible_v2()),
    pytest.param(slice(0, 2), 2, marks=pytest.mark.requires_ansible_v1()),
    pytest.param(slice(0, 2), 3, marks=pytest.mark.requires_ansible_v2()),
    (slice(0), 1),
    (slice(1), 1),
    (slice(2), 1),
    (slice(3), 1),
]

NEGATIVE_HOST_SLICES = [
    slice(None),
    slice(-1),
]


def pytest_runtest_setup(item):
    # Conditionally skip tests that are pinned to a specific ansible version
    if isinstance(item, pytest.Function):
        # conditionally skip
        if item.get_closest_marker("requires_ansible_v1") and not has_ansible_v1:
            pytest.skip("requires < ansible-2.*")
        if item.get_closest_marker("requires_ansible_v2") and has_ansible_v1:
            pytest.skip("requires >= ansible-2.*")
        if item.get_closest_marker("requires_ansible_v24") and not has_ansible_v24:
            pytest.skip("requires >= ansible-2.4.*")
        if item.get_closest_marker("requires_ansible_v28") and not has_ansible_v24:
            pytest.skip("requires >= ansible-2.8.*")

        # conditionally xfail
        mark = item.get_closest_marker("ansible_v1_xfail")
        if mark and has_ansible_v1:
            item.add_marker(
                pytest.mark.xfail(
                    reason="expected failure on < ansible-2.*",
                    raises=mark.kwargs.get("raises"),
                ),
            )

        mark = item.get_closest_marker("ansible_v2_xfail")
        if mark and not has_ansible_v1:
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
