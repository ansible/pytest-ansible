import pytest
try:
    from _pytest.main import EXIT_OK
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
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'local'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_ansible_module(testdir, option):
    src = """
        import pytest
        from pytest_ansible.module_dispatcher import BaseModuleDispatcher
        def test_func(ansible_module):
            assert isinstance(ansible_module, BaseModuleDispatcher)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'local'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_ansible_facts(testdir, option):
    src = """
        import pytest
        from pytest_ansible.results import AdHocResult
        def test_func(ansible_facts):
            assert isinstance(ansible_facts, AdHocResult)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'local'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


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
    assert result.parseoutcomes()['passed'] == 1


def test_ansible_host(testdir, option):
    src = """
        import pytest
        from pytest_ansible.module_dispatcher import BaseModuleDispatcher
        def test_func(ansible_host):
            assert isinstance(ansible_host, BaseModuleDispatcher)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'all'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 8


# NOTE: ansible-v1.9 will fail with a KeyError when attempting hosts['ungrouped'].  This surfaces as a AssertionError in
# the following test.
@pytest.mark.ansible_v1_xfail(raises=AssertionError)
def test_ansible_group(testdir, option):
    src = """
        import pytest
        from pytest_ansible.module_dispatcher import BaseModuleDispatcher
        def test_func(ansible_group):
            assert isinstance(ansible_group, BaseModuleDispatcher)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'all'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 5
