from _pytest.main import EXIT_OK, EXIT_TESTSFAILED, EXIT_USAGEERROR, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED  # NOQA


def test_contacted_with_params(testdir, option):
    """FIXME
    """
    src = """
        import pytest
        def test_func(ansible_module):
            contacted = ansible_module.ping()

            # assert contacted hosts ...
            assert contacted
            assert len(contacted) == len(ansible_module.inventory_manager.list_hosts('local'))
            for result in contacted.values():
                assert 'failed' not in result
                assert 'invocation' in result
                assert 'module_name' in result['invocation']
                assert 'ping' == result['invocation']['module_name']

    """
    testdir.makepyfile(src)
    print(option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'local'])
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'local'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_contacted_with_params_and_inventory_marker(testdir, option):
    """FIXME
    """
    src = """
        import pytest
        @pytest.mark.ansible(inventory='%s')
        def test_func(ansible_module):
            contacted = ansible_module.ping()

            # assert contacted hosts ...
            assert contacted
            assert len(contacted) == len(ansible_module.inventory_manager.list_hosts('local'))
            for result in contacted.values():
                assert 'failed' not in result
                assert 'invocation' in result
                assert 'module_name' in result['invocation']
                assert 'ping' == result['invocation']['module_name']

    """ % str(option.inventory)
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-host-pattern', 'local'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_contacted_with_params_and_host_pattern_marker(testdir, option):
    """FIXME
    """
    src = """
        import pytest
        @pytest.mark.ansible(host_pattern='local')
        def test_func(ansible_module):
            contacted = ansible_module.ping()

            # assert contacted hosts ...
            assert contacted
            assert len(contacted) == len(ansible_module.inventory_manager.list_hosts('local'))
            for result in contacted.values():
                assert 'failed' not in result
                assert 'invocation' in result
                assert 'module_name' in result['invocation']
                assert 'ping' == result['invocation']['module_name']

    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'unreachable'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_contacted_with_params_and_inventory_host_pattern_marker(testdir, option):
    """FIXME
    """
    src = """
        import pytest
        @pytest.mark.ansible(inventory='%s', host_pattern='local')
        def test_func(ansible_module):
            contacted = ansible_module.ping()

            # assert contacted hosts ...
            assert contacted
            assert len(contacted) == len(ansible_module.inventory_manager.list_hosts('local'))
            for result in contacted.values():
                assert 'failed' not in result
                assert 'invocation' in result
                assert 'module_name' in result['invocation']
                assert 'ping' == result['invocation']['module_name']

    """ % str(option.inventory)
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', '/dev/null', '--ansible-host-pattern', 'unreachable'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_become(testdir, option):
    """Test --ansible-become* parameters.  This test doesn't actually 'sudo',
    but verifies that 'sudo' was attempted by asserting
    '--ansible-become-user=<bogus_username>' fails as expected.
    """
    src = """
        import pytest
        import ansible
        import re
        import os
        @pytest.mark.ansible(inventory='%s', host_pattern='localhost')
        def test_func(ansible_module):
            contacted = ansible_module.ping()

            # assert contacted hosts ...
            assert contacted
            assert len(contacted) == len(ansible_module.inventory_manager.list_hosts('localhost'))
            for result in contacted.values():
                assert 'failed' in result, "Missing expected field in JSON response: failed"
                assert result['failed'], "Test did not fail as expected"
                if ansible.__version__.startswith('2'):
                    assert 'module_stderr' in result
                    assert 'sudo: unknown user: asdfasdf' in result['module_stderr']
                    # assert 'sudo: a password is required' in result['module_stderr']
                else:
                    assert 'msg' in result, "Missing expected field in JSON response: msg"
                    assert 'sudo: unknown user: asdfasdf' in result['msg']
                    # assert re.match('\[sudo via ansible, [^\]]*\] password:', result['msg']) is not None
                    # "sudo: must be setuid root"

    """ % str(option.inventory)
    testdir.makepyfile(src)
    result = testdir.runpytest(
        *option.args + [
            '--ansible-inventory', str(option.inventory),
            '--ansible-host-pattern', 'localhost',  # run against a single host
            '--ansible-become',  # Enable become support
            '--ansible-become-user', 'asdfasdf'  # Connect using a bogus username
        ]
    )
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_dark_with_params(testdir, option):
    """FIXME
    """
    src = """
        import pytest
        from pytest_ansible.errors import (AnsibleHostUnreachable, AnsibleNoHostsMatch)
        def test_func(ansible_module):
            exc_info = pytest.raises(AnsibleHostUnreachable, ansible_module.ping)
            (contacted, dark) = exc_info.value.results

            # assert no contacted hosts ...
            assert not contacted, "%d hosts were contacted, expected %d" \
                % (len(contacted), 0)

            # assert dark hosts ...
            assert dark
            assert len(dark) == len(ansible_module.inventory_manager.list_hosts('unreachable'))
            for result in dark.values():
                assert 'failed' in result or 'unreachable' in result
                assert result.get('failed', False) or result.get('unreachable', False)
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'unreachable'])
    print "\n".join(result.stdout.lines)
    print "\n".join(result.stderr.lines)
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_dark_with_params_and_inventory_marker(testdir, option):
    """FIXME
    """
    src = """
        import pytest
        from pytest_ansible.errors import (AnsibleHostUnreachable, AnsibleNoHostsMatch)
        @pytest.mark.ansible(inventory='{inventory}')
        def test_func(ansible_module):
            exc_info = pytest.raises(AnsibleHostUnreachable, ansible_module.ping)
            (contacted, dark) = exc_info.value.results

            # assert no contacted hosts ...
            assert not contacted, "%d hosts were contacted, expected %d" \
                % (len(contacted), 0)

            # assert dark hosts ...
            assert dark
            assert len(dark) == len(ansible_module.inventory_manager.list_hosts('unreachable'))
            for result in dark.values():
                assert 'failed' in result or 'unreachable' in result
                assert result.get('failed', False) or result.get('unreachable', False)
    """.format(inventory=str(option.inventory))
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-host-pattern', 'unreachable'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_dark_with_params_and_host_pattern_marker(testdir, option):
    """FIXME
    """
    src = """
        import pytest
        import ansible
        from pytest_ansible.errors import (AnsibleHostUnreachable, AnsibleNoHostsMatch)
        @pytest.mark.ansible(host_pattern='unreachable')
        def test_func(ansible_module):
            exc_info = pytest.raises(AnsibleHostUnreachable, ansible_module.ping)
            (contacted, dark) = exc_info.value.results

            # assert no contacted hosts ...
            assert not contacted, "%d hosts were contacted, expected %d" \
                % (len(contacted), 0)

            # assert dark hosts ...
            assert dark
            assert len(dark) == len(ansible_module.inventory_manager.list_hosts('unreachable'))
            for result in dark.values():
                assert 'failed' in result or 'unreachable' in result
                assert result.get('failed', False) or result.get('unreachable', False)
                if ansible.__version__.startswith('2'):
                    assert 'SSH encountered an unknown error' in result['msg']
                else:
                    assert result['msg'].startswith('SSH Error: ssh: Could not resolve hostname')
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'local'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_dark_with_debug_enabled(testdir, option):
    """Verify that when --ansible-debug is provide, additional output is provided upon host failure.
    """
    src = """
        import pytest
        from pytest_ansible.errors import AnsibleHostUnreachable
        def test_func(ansible_module):
            ansible_module.ping()
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory),
                                               '--ansible-host-pattern', 'unreachable',
                                               '--ansible-debug'])
    assert result.ret == EXIT_TESTSFAILED
    assert result.parseoutcomes()['failed'] == 1
    # FIXME - the following doesn't work on ansible-v2
    # result.stdout.fnmatch_lines([
    #     '*ESTABLISH CONNECTION FOR USER: *',
    #     '*REMOTE_MODULE ping',
    #     '*EXEC ssh *',
    # ])
