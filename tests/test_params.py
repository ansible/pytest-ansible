import pytest
import ansible
import mock
from _pytest.main import EXIT_OK, EXIT_TESTSFAILED, EXIT_USAGEERROR, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED


def test_plugin_help(testdir):
    """Verifies expected output from of py.test --help"""

    result = testdir.runpytest('--help')
    result.stdout.fnmatch_lines([
        # Check for the github args section header
        'pytest-ansible:',
        # Check for the specific args
        '  --ansible-inventory=ANSIBLE_INVENTORY',
        '  --ansible-host-pattern=ANSIBLE_HOST_PATTERN',
        '  --ansible-connection=ANSIBLE_CONNECTION',
        '  --ansible-user=ANSIBLE_USER',
        '  --ansible-debug *',
        '  --ansible-sudo *',
        '  --ansible-sudo-user=ANSIBLE_SUDO_USER',
        '  --ansible-become *',
        '  --ansible-become-method=ANSIBLE_BECOME_METHOD',
        '  --ansible-become-user=ANSIBLE_BECOME_USER',
        # Check for the marker in --help
        '  ansible (args) * Ansible integration',
    ])


def test_plugin_markers(testdir):
    """Verifies expected output from of py.test --markers"""

    result = testdir.runpytest('--markers')
    result.stdout.fnmatch_lines([
        '@pytest.mark.ansible(*args): Ansible integration',
    ])


def test_report_header(testdir, option):
    """Verify the expected ansible version in the pytest report header.
    """

    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_NOTESTSCOLLECTED
    result.stdout.fnmatch_lines([
        'ansible: %s' % ansible.__version__,
    ])


def test_params_not_required_when_not_using_fixture(testdir, option):
    """Verify the ansible parameters are not required if the fixture is not used.
    """

    src = """
        import pytest
        def test_func():
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_OK


def test_params_required_when_using_fixture(testdir, option):
    """Verify the ansible parameters are required if the fixture is used.
    """

    src = """
        import pytest
        def test_func(ansible_module):
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines([
        'ERROR: Missing required parameter --ansible-host-pattern',
    ])


def test_params_required_with_host_generator(testdir, option):
    """Verify the ansible parameters are required if the fixture is used.
    """

    src = """
        import pytest
        def test_func(ansible_host):
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_TESTSFAILED
    result.stdout.fnmatch_lines([
        'collected 0 items / 1 errors',
        'E   UsageError: Missing required parameter --ansible-host-pattern',
    ])


def test_params_required_with_group_generator(testdir, option):
    """Verify the ansible parameters are required if the fixture is used.
    """

    src = """
        import pytest
        def test_func(ansible_group):
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args)
    assert result.ret == EXIT_TESTSFAILED
    result.stdout.fnmatch_lines([
        'collected 0 items / 1 errors',
        'E   UsageError: Missing required parameter --ansible-host-pattern',
    ])


@pytest.mark.parametrize(
    "required_value_parameter",
    [
        '--ansible-inventory',
        '--ansible-host-pattern',
        '--ansible-connection',
        '--ansible-user',
        '--ansible-sudo-user',
        '--ansible-become-method',
        '--ansible-become-user',
    ],
)
def test_param_requires_value(testdir, required_value_parameter):
    """Verifies failure when not providing a value to a parameter that requires a value"""

    result = testdir.runpytest(*[required_value_parameter])
    assert result.ret == EXIT_INTERRUPTED
    result.stderr.fnmatch_lines([
        '*: error: argument %s: expected one argument' % required_value_parameter,
    ])


def test_params_required_with_inventory_without_host_pattern(testdir, option):
    src = """
        import pytest
        def test_func(ansible_module):
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-inventory', 'local,'])
    assert result.ret == EXIT_USAGEERROR
    result.stderr.fnmatch_lines([
        'ERROR: Missing required parameter --ansible-host-pattern',
    ])


@pytest.mark.requires_ansible_v1
def test_params_required_with_bogus_inventory_v1(testdir, option):
    src = """
        import pytest
        def test_func(ansible_module):
            assert True
    """
    testdir.makepyfile(src)
    with mock.patch('os.path.isfile', return_value=False) as mock_isfile:
        result = testdir.runpytest(*option.args + ['--ansible-inventory', 'bogus', '--ansible-host-pattern', 'all'])

    # Assert py.test exit code
    assert result.ret == EXIT_TESTSFAILED
    result.stdout.fnmatch_lines([
        'UsageError: Unable to find an inventory file, specify one with -i ?',
    ])

    # Assert mock open called on provided file
    mock_isfile.assert_called_with('bogus')


@pytest.mark.requires_ansible_v2
def test_params_required_with_bogus_inventory_v2(testdir, option, recwarn):
    src = """
        import pytest
        def test_func(ansible_module):
            assert True
    """
    testdir.makepyfile(src)
    with mock.patch('os.path.isfile', return_value=False) as mock_isfile:
        result = testdir.runpytest(*['-vs', '--ansible-inventory', 'bogus', '--ansible-host-pattern', 'all'])

    # Assert py.test exit code
    assert result.ret == EXIT_OK

    # Assert mock open called on provided file
    mock_isfile.assert_called_with('bogus')

    # TODO - assert the following warning appears
    # [WARNING]: provided hosts list is empty, only localhost is available"
    if False:
        result.stderr.fnmatch_lines(
            [
                "*provided hosts list is empty, only localhost is available",
            ]
        )


@pytest.mark.requires_ansible_v1
def test_params_required_without_inventory_with_host_pattern_v1(testdir, option):
    src = """
        import pytest
        def test_func(ansible_module):
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-host-pattern', 'all'])
    assert result.ret == EXIT_TESTSFAILED
    result.stdout.fnmatch_lines([
        'UsageError: Unable to find an inventory file, specify one with -i ?',
    ])


@pytest.mark.requires_ansible_v2
def test_params_required_without_inventory_with_host_pattern_v2(testdir, option):
    src = """
        import pytest
        def test_func(ansible_module):
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*option.args + ['--ansible-host-pattern', 'all'])
    assert result.ret == EXIT_OK

    # TODO - validate the following warning message
    # [WARNING]: provided hosts list is empty, only localhost is available
    if False:
        result.stderr.fnmatch_lines(
            [
                "*provided hosts list is empty, only localhost is available",
            ]
        )


def test_param_override_with_marker(testdir):
    src = """
        import pytest
        @pytest.mark.ansible(ansible_inventory='local,', ansible_connection='local',
        def test_func(ansible_module):
            assert True
    """
    testdir.makepyfile(src)
    result = testdir.runpytest(*['--ansible-inventory', 'garbage', '--ansible-host-pattern', 'garbage'])
    assert result.ret == EXIT_OK

    # Mock assert the correct variables are set
