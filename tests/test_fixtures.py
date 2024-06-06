try:  # noqa: INP001, D100
    from _pytest.main import EXIT_OK  # type: ignore  # noqa: PGH003
except ImportError:
    from _pytest.main import ExitCode  # type: ignore[attr-defined]

    EXIT_OK = ExitCode.OK


def test_ansible_adhoc(pytester, option):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    src = """
        import pytest
        import types
        from pytest_ansible.host_manager.base import BaseHostManager
        def test_func(ansible_adhoc):
            assert isinstance(ansible_adhoc, types.FunctionType)
            assert isinstance(ansible_adhoc(), BaseHostManager)
    """
    pytester.makepyfile(src)
    result = pytester.runpytest(
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


def test_ansible_module(pytester, option):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    src = """
        import pytest
        from pytest_ansible.module_dispatcher import BaseModuleDispatcher
        def test_func(ansible_module):
            assert isinstance(ansible_module, BaseModuleDispatcher)
    """
    pytester.makepyfile(src)
    result = pytester.runpytest(
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


def test_ansible_facts(pytester, option):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    src = """
        import pytest
        from pytest_ansible.results import AdHocResult
        def test_func(ansible_facts):
            assert isinstance(ansible_facts, AdHocResult)
    """
    pytester.makepyfile(src)
    result = pytester.runpytest(
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


def test_localhost(pytester, option):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    src = """
        import pytest
        from pytest_ansible.module_dispatcher import BaseModuleDispatcher
        def test_func(localhost):
            assert isinstance(localhost, BaseModuleDispatcher)
    """
    pytester.makepyfile(src)
    result = pytester.runpytest(*option.args)
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()["passed"] == 1
