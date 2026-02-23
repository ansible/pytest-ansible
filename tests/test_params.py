"""Test CLI parameters."""

from __future__ import annotations

import warnings

from typing import TYPE_CHECKING

import ansible
import pytest


if TYPE_CHECKING:
    from tests.conftest import PyTestOption


# pylint: disable=unused-import
try:
    from _pytest.main import (  # type: ignore[attr-defined]
        EXIT_INTERRUPTED,
        EXIT_NOTESTSCOLLECTED,
        EXIT_OK,
        EXIT_TESTSFAILED,
        EXIT_USAGEERROR,
    )
except ImportError:
    from _pytest.main import ExitCode  # type: ignore[attr-defined]

    EXIT_OK = ExitCode.OK
    EXIT_TESTSFAILED = ExitCode.TESTS_FAILED
    EXIT_USAGEERROR = ExitCode.USAGE_ERROR
    EXIT_INTERRUPTED = ExitCode.INTERRUPTED
    EXIT_NOTESTSCOLLECTED = ExitCode.NO_TESTS_COLLECTED


def test_plugin_help(pytester):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Verifies expected output from of pytest --help."""
    result = pytester.runpytest("--help")
    result.stdout.fnmatch_lines(
        [
            # Check for the github args section header
            "pytest-ansible:",
            # Check for the specific args
            "  --inventory*, --ansible-inventory=ANSIBLE_INVENTORY",
            "  --host-pattern*, --ansible-host-pattern=ANSIBLE_HOST_PATTERN",
            "  --ansible-connection=ANSIBLE_CONNECTION",
            "  --user*, --ansible-user=ANSIBLE_USER",
            "  --check, --ansible-check",
            "  --module-path*, --ansible-module-path=ANSIBLE_MODULE_PATH",
            "  --become, --ansible-become",
            "  --become-method*, --ansible-become-method=ANSIBLE_BECOME_METHOD",
            "  --become-user*, --ansible-become-user=ANSIBLE_BECOME_USER",
            "  --ask-become-pass*, --ansible-ask-become-pass=ANSIBLE_ASK_BECOME_PASS",
            # Check for the marker in --help
            "  ansible (args)*Ansible integration",
        ],
    )


def test_plugin_markers(pytester):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Verifies expected output from of pytest --markers."""
    result = pytester.runpytest("--markers")
    result.stdout.fnmatch_lines(
        [
            "@pytest.mark.ansible(*args): Ansible integration",
        ],
    )


def test_report_header(pytester, option):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Verify the expected ansible version in the pytest report header."""
    result = pytester.runpytest(*option.args)
    assert result.ret == EXIT_NOTESTSCOLLECTED
    result.stdout.fnmatch_lines([f"ansible: {ansible.__version__}"])


def test_params_not_required_when_not_using_fixture(pytester, option):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Verify the ansible parameters are not required if the fixture is not used."""
    src = """
        import pytest
        def test_func():
            assert True
    """
    pytester.makepyfile(src)
    result = pytester.runpytest(*option.args)
    assert result.ret == EXIT_OK


@pytest.mark.parametrize(
    "fixture_name",
    (
        "ansible_adhoc",
        "ansible_module",
        "ansible_facts",
    ),
)
def test_params_required_when_using_fixture(
    pytester: pytest.Pytester,
    option: PyTestOption,
    fixture_name: str,
) -> None:
    """Verify that ansible parameters are not required if the fixture is used.

    Args:
        pytester: fixture
        option: fixture
        fixture_name: string
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)

        src = f"""
            import pytest
            def test_func({fixture_name}):
                {fixture_name}
            """

        pytester.makepyfile(src)
        result = pytester.runpytest(*option.args)
        assert result.ret == EXIT_OK


@pytest.mark.parametrize(
    "required_value_parameter",
    (
        "--ansible-inventory",
        "--inventory",
        "--ansible-connection",
        "--ansible-user",
        "--user",
        "--ansible-become-method",
        "--become-method",
        "--ansible-become-user",
        "--become-user",
        "--ansible-module-path",
        "--module-path",
    ),
)
def test_param_requires_value(pytester, required_value_parameter):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Verifies failure when not providing a value to a parameter that requires a value."""
    result = pytester.runpytest(*[required_value_parameter])
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(
        [f"*: error: argument *{required_value_parameter}*: expected one argument"],
    )


@pytest.mark.requires_ansible_v2
def test_params_required_without_inventory_with_host_pattern_v2(pytester, option):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    src = """
        import pytest
        def test_func(ansible_module):
            assert True
    """
    pytester.makepyfile(src)
    result = pytester.runpytest(*[*option.args, "--ansible-host-pattern", "all"])
    assert result.ret == EXIT_OK


def test_param_override_with_marker(pytester, option):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    src = """
        import pytest
        @pytest.mark.ansible(inventory='local,', connection='local', host_pattern='all')
        def test_func(ansible_module):
            ansible_module.ping()
    """
    pytester.makepyfile(src)
    result = pytester.runpytest(
        *[
            *option.args,
            "--tb",
            "native",
            "--ansible-inventory",
            "garbage,",
            "--ansible-host-pattern",
            "garbage",
            "--ansible-connection",
            "garbage",
        ],
    )
    assert result.ret == EXIT_OK

    # Mock assert the correct variables are set


def test_deprecated_connection_warning() -> None:
    """Verify a deprecation warning is emitted when --connection is used."""
    from pytest_ansible.plugin import pytest_load_initial_conftests

    args: list[str] = ["--connection", "local"]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        pytest_load_initial_conftests(early_config=None, parser=None, args=args)  # type: ignore[arg-type]

    assert len(caught) == 1
    assert issubclass(caught[0].category, DeprecationWarning)
    assert "pytest-ansible no longer supports the '--connection' option" in str(caught[0].message)


def test_no_warning_without_connection_flag() -> None:
    """Verify no warning is emitted when --connection is not used."""
    from pytest_ansible.plugin import pytest_load_initial_conftests

    args: list[str] = ["--ansible-connection", "local"]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        pytest_load_initial_conftests(early_config=None, parser=None, args=args)  # type: ignore[arg-type]

    assert len(caught) == 0


def test_deprecated_connection_warning_integration(
    pytester: pytest.Pytester,
) -> None:
    """Integration test: verify deprecation warning appears when --connection is used.

    Args:
        pytester: pytest fixture for running pytest in a subprocess
    """
    pytester.makeconftest(
        """
        def pytest_addoption(parser):
            parser.addoption("--connection", action="store", default=None)
        """,
    )
    pytester.makepyfile(
        """
        def test_func():
            assert True
        """,
    )
    result = pytester.runpytest("--connection", "local", "-W", "all::DeprecationWarning")
    result.stdout.fnmatch_lines(
        ["*pytest-ansible no longer supports the '--connection' option*"],
    )
