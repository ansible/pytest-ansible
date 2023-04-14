# pylint: disable=unused-import


try:
    from _pytest.main import EXIT_OK  # type: ignore
except ImportError:
    from _pytest.main import ExitCode

    EXIT_OK = ExitCode.OK


def test_ansible_adhoc(testdir, option):
    src = """
        import pytest
        import types
        from pytest_ansible.host_manager import BaseHostManager
        def test_func(ansible_adhoc):
            assert isinstance(ansible_adhoc, types.FunctionType)
            assert isinstance(ansible_adhoc(), BaseHostManager)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(
        *[
            *option.args,
            "--ansible-inventory",
            str(option.inventory),
            "--ansible-host-pattern",
            "local",
        ],
    )
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()["passed"] == 1


def test_ansible_module(testdir, option):
    src = """
        import pytest
        from pytest_ansible.module_dispatcher import BaseModuleDispatcher
        def test_func(ansible_module):
            assert isinstance(ansible_module, BaseModuleDispatcher)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(
        *[
            *option.args,
            "--ansible-inventory",
            str(option.inventory),
            "--ansible-host-pattern",
            "local",
        ],
    )
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()["passed"] == 1


def test_ansible_facts(testdir, option):
    src = """
        import pytest
        from pytest_ansible.results import AdHocResult
        def test_func(ansible_facts):
            assert isinstance(ansible_facts, AdHocResult)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(
        *[
            *option.args,
            "--ansible-inventory",
            str(option.inventory),
            "--ansible-host-pattern",
            "local",
        ],
    )
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()["passed"] == 1


def test_localhost(testdir, option):
    src = """
        import pytest
        from pytest_ansible.module_dispatcher import BaseModuleDispatcher
        def test_func(localhost):
            assert isinstance(localhost, BaseModuleDispatcher)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()["passed"] == 1
