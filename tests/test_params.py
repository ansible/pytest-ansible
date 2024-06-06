import ansible  # noqa: INP001, D100
import pytest


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
            "  --inventory=ANSIBLE_INVENTORY, --ansible-inventory=ANSIBLE_INVENTORY",
            "  --host-pattern=ANSIBLE_HOST_PATTERN, --ansible-host-pattern=ANSIBLE_HOST_PATTERN",
            "  --connection=ANSIBLE_CONNECTION, --ansible-connection=ANSIBLE_CONNECTION",
            "  --user=ANSIBLE_USER, --ansible-user=ANSIBLE_USER",
            "  --check, --ansible-check",
            "  --module-path=ANSIBLE_MODULE_PATH, --ansible-module-path=ANSIBLE_MODULE_PATH",
            "  --become, --ansible-become",
            "  --become-method=ANSIBLE_BECOME_METHOD, --ansible-become-method=ANSIBLE_BECOME_METHOD",  # noqa: E501
            "  --become-user=ANSIBLE_BECOME_USER, --ansible-become-user=ANSIBLE_BECOME_USER",
            "  --ask-become-pass=ANSIBLE_ASK_BECOME_PASS, --ansible-ask-become-pass=ANSIBLE_ASK_BECOME_PASS",  # noqa: E501
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
def test_params_required_when_using_fixture(pytester, option, fixture_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Verify the ansible parameters are required if the fixture is used."""
    src = f"""
        import pytest
        def test_func({fixture_name}):
            {fixture_name}
        """

    pytester.makepyfile(src)
    result = pytester.runpytest(*option.args)
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(
        [
            "ERROR: Missing required parameter --ansible-host-pattern/--host-pattern",
        ],
    )


@pytest.mark.parametrize(
    "required_value_parameter",
    (
        "--ansible-inventory",
        "--inventory",
        "--ansible-host-pattern",
        "--host-pattern",
        "--ansible-connection",
        "--connection",
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


def test_params_required_with_inventory_without_host_pattern(pytester, option):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Verify that a host pattern is required when an inventory is supplied."""
    src = """
        import pytest
        def test_func(ansible_module):
            assert True
    """
    pytester.makepyfile(src)
    result = pytester.runpytest(*[*option.args, "--ansible-inventory", "local,"])
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(
        [
            "ERROR: Missing required parameter --ansible-host-pattern/--host-pattern",
        ],
    )


@pytest.mark.requires_ansible_v2()
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
