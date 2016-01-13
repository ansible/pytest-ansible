import pytest
from pkg_resources import parse_version
from _pytest.main import EXIT_OK, EXIT_TESTSFAILED, EXIT_USAGEERROR, EXIT_NOTESTSCOLLECTED

# Indicate whether ansible-2.* is available
import ansible
requires_ansible_v1 = pytest.mark.skipif(parse_version(ansible.__version__) >= parse_version('2.0.0'),
                                         reason="requires ansible-1.*")
requires_ansible_v2 = pytest.mark.skipif(parse_version(ansible.__version__) < parse_version('2.0.0'),
                                         reason="requires ansible-2.*")

pytest_plugins = 'pytester',


class PyTestOption(object):

    def __init__(self, config, testdir):
        self.config = config

        # Create inventory file
        self.inventory = testdir.makefile('.ini', inventory='''
            [local]
            localhost ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.2 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.3 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.4 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.5 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'

            [unreachable]
            unreachable-host-1.example.com
            unreachable-host-2.example.com
            unreachable-host-3.example.com
        ''')

        # Create ansible.cfg file
        # self.ansible_cfg = testdir.makefile('.cfg', ansible='''[ssh_connection]\ncontrol_path = %(directory)s/%%h-%%r''')

    @property
    def args(self):
        args = list()
        args.append('--tb')
        args.append('native')
        return args


@pytest.fixture()
def option(request, testdir):
    '''Returns an instance of PyTestOption to help tests pass parameters and
    use a common inventory file.
    '''
    return PyTestOption(request.config, testdir)


def test_report_header(testdir, option):
    '''Verify the expected ansible version in the pytest report header.
    '''

    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_NOTESTSCOLLECTED
    print '\n'.join(result.stdout.lines)
    print '\n'.join(result.stderr.lines)
    print result.stderr.lines
    result.stdout.fnmatch_lines([
        'ansible: %s' % ansible.__version__,
    ])


def test_params_not_required(testdir, option):
    '''Verify the ansible parameters are not required if the fixture is not used.
    '''

    src = '''
        import pytest
        def test_func():
            assert True
    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_OK


def test_params_required(testdir, option):
    '''Verify the ansible parameters are required if the fixture is used.
    '''

    src = '''
        import pytest
        def test_func(ansible_module):
            assert True
    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines([
        'ERROR: Missing required parameter --ansible-host-pattern',
    ])


def test_params_required_with_host_generator(testdir, option):
    '''Verify the ansible parameters are required if the fixture is used.
    '''

    src = '''
        import pytest
        def test_func(ansible_host):
            assert True
    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_TESTSFAILED
    result.stdout.fnmatch_lines([
        'collected 0 items / 1 errors',
        'E   UsageError: Missing required parameter --ansible-host-pattern',
    ])


def test_params_required_with_group_generator(testdir, option):
    '''Verify the ansible parameters are required if the fixture is used.
    '''

    src = '''
        import pytest
        def test_func(ansible_group):
            assert True
    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_TESTSFAILED
    result.stdout.fnmatch_lines([
        'collected 0 items / 1 errors',
        'E   UsageError: Missing required parameter --ansible-host-pattern',
    ])


def test_params_required_with_inventory_without_host_pattern(testdir, option):
    src = '''
        import pytest
        def test_func(ansible_module):
            assert True
    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', 'local,'])
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines([
        'ERROR: Missing required parameter --ansible-host-pattern',
    ])


@requires_ansible_v1
def test_params_required_with_bogus_inventory_v1(testdir, option):
    src = '''
        import pytest
        def test_func(ansible_module):
            assert True
    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', 'no such file', '--ansible-host-pattern', 'all'])
    assert result.ret == EXIT_TESTSFAILED
    result.stdout.fnmatch_lines([
        'UsageError: Unable to find an inventory file, specify one with -i ?',
        # 'UsageError: ERROR! Unable to find an inventory file (no such file), specify one with -i ?',]
    ])


@requires_ansible_v2
def test_params_required_with_bogus_inventory_v2(testdir, option):
    src = '''
        import pytest
        def test_func(ansible_module):
            assert True
    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', 'no such file', '--ansible-host-pattern', 'all'])
    assert result.ret == EXIT_OK
    # TODO - assert the following warning appears
    # [WARNING]: provided hosts list is empty, only localhost is available"


@requires_ansible_v1
def test_params_required_without_inventory_with_host_pattern_v1(testdir, option):
    src = '''
        import pytest
        def test_func(ansible_module):
            assert True
    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-host-pattern', 'all'])
    assert result.ret == EXIT_TESTSFAILED
    result.stdout.fnmatch_lines([
        'UsageError: Unable to find an inventory file, specify one with -i ?',
    ])


@requires_ansible_v2
def test_params_required_without_inventory_with_host_pattern_v2(testdir, option):
    src = '''
        import pytest
        def test_func(ansible_module):
            assert True
    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-host-pattern', 'all'])
    assert result.ret == EXIT_OK

    # TODO - validate the following warning message
    # [WARNING]: provided hosts list is empty, only localhost is available


def test_contacted_with_params(testdir, option):
    '''FIXME
    '''
    src = '''
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

    '''
    testdir.makepyfile(src)
    print(option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'local'])
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'local'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_contacted_with_params_and_inventory_marker(testdir, option):
    '''FIXME
    '''
    src = '''
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

    ''' % str(option.inventory)
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-host-pattern', 'local'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_contacted_with_params_and_host_pattern_marker(testdir, option):
    '''FIXME
    '''
    src = '''
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

    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'unreachable'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_contacted_with_params_and_inventory_host_pattern_marker(testdir, option):
    '''FIXME
    '''
    src = '''
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

    ''' % str(option.inventory)
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', '/dev/null', '--ansible-host-pattern', 'unreachable'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_dark_with_params(testdir, option):
    '''FIXME
    '''
    src = '''
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
    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'unreachable'])
    print "\n".join(result.stdout.lines)
    print "\n".join(result.stderr.lines)
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_dark_with_params_and_inventory_marker(testdir, option):
    '''FIXME
    '''
    src = '''
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
    '''.format(inventory=str(option.inventory))
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-host-pattern', 'unreachable'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_dark_with_params_and_host_pattern_marker(testdir, option):
    '''FIXME
    '''
    src = '''
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
                print result['msg']
                if ansible.__version__.startswith('2'):
                    assert result['msg'].startswith('ERROR! SSH encountered an unknown error')
                else:
                    assert result['msg'].startswith('SSH Error: ssh: Could not resolve hostname')
    '''
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', str(option.inventory), '--ansible-host-pattern', 'local'])
    assert result.ret == EXIT_OK
    assert result.parseoutcomes()['passed'] == 1


def test_dark_with_debug_enabled(testdir, option):
    '''Verify that when --ansible-debug is provide, additional output is provided upon host failure.
    '''
    src = '''
        import pytest
        from pytest_ansible.errors import AnsibleHostUnreachable
        def test_func(ansible_module):
            ansible_module.ping()
    '''
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
