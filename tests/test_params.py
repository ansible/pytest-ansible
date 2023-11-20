import ansible
import pytest


# pylint: disable=unused-import
try:
    from _pytest.main import (
        EXIT_INTERRUPTED,  # type: ignore[attr-defined]
        EXIT_NOTESTSCOLLECTED,  # type: ignore[attr-defined]
        EXIT_OK,  # type: ignore[attr-defined]
        EXIT_TESTSFAILED,  # type: ignore[attr-defined]
        EXIT_USAGEERROR,  # type: ignore[attr-defined]
    )
except ImportError:
    from _pytest.main import ExitCode

    EXIT_OK = ExitCode.OK
    EXIT_TESTSFAILED = ExitCode.TESTS_FAILED
    EXIT_USAGEERROR = ExitCode.USAGE_ERROR
    EXIT_INTERRUPTED = ExitCode.INTERRUPTED
    EXIT_NOTESTSCOLLECTED = ExitCode.NO_TESTS_COLLECTED


def test_plugin_help(testdir):
    """Verifies expected output from of pytest --help."""
    result = testdir.runpytest("--help")
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
            "  --become-method=ANSIBLE_BECOME_METHOD, --ansible-become-method=ANSIBLE_BECOME_METHOD",
            "  --become-user=ANSIBLE_BECOME_USER, --ansible-become-user=ANSIBLE_BECOME_USER",
            "  --ask-become-pass=ANSIBLE_ASK_BECOME_PASS, --ansible-ask-become-pass=ANSIBLE_ASK_BECOME_PASS",
            # Check for the marker in --help
            "  ansible (args)*Ansible integration",
        ],
    )


def test_plugin_markers(testdir):
    """Verifies expected output from of pytest --markers."""
    result = testdir.runpytest("--markers")
    result.stdout.fnmatch_lines(
        [
            "@pytest.mark.ansible(*args): Ansible integration",
        ],
    )


def test_report_header(testdir, option):
    """Verify the expected ansible version in the pytest report header."""
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_NOTESTSCOLLECTED
    result.stdout.fnmatch_lines([f"ansible: {ansible.__version__}"])


def test_params_not_required_when_not_using_fixture(testdir, option):
    """Verify the ansible parameters are not required if the fixture is not used."""
    src = """
        import pytest
        def test_func():
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_OK


@pytest.mark.parametrize(
    "fixture_name",
    (
        "ansible_adhoc",
        "ansible_module",
        "ansible_facts",
    ),
)
def test_params_required_when_using_fixture(testdir, option, fixture_name):
    """Verify the ansible parameters are required if the fixture is used."""
    src = f"""
        import pytest
        def test_func({fixture_name}):
            {fixture_name}
        """

    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
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
def test_param_requires_value(testdir, required_value_parameter):
    """Verifies failure when not providing a value to a parameter that requires a value."""
    result = testdir.runpytest(*[required_value_parameter])
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(
        [f"*: error: argument *{required_value_parameter}*: expected one argument"],
    )


def test_params_required_with_inventory_without_host_pattern(testdir, option):
    """Verify that a host pattern is required when an inventory is supplied."""
    src = """
        import pytest
        def test_func(ansible_module):
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*[*option.args, "--ansible-inventory", "local,"])
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines(
        [
            "ERROR: Missing required parameter --ansible-host-pattern/--host-pattern",
        ],
    )


@pytest.mark.requires_ansible_v2()
def test_params_required_without_inventory_with_host_pattern_v2(testdir, option):
    src = """
        import pytest
        def test_func(ansible_module):
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*[*option.args, "--ansible-host-pattern", "all"])
    assert result.ret == EXIT_OK


def test_param_override_with_marker(testdir, option):
    src = """
        import pytest
        @pytest.mark.ansible(inventory='local,', connection='local', host_pattern='all')
        def test_func(ansible_module):
            ansible_module.ping()
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(
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
