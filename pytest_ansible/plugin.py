import pytest
from pkg_resources import parse_version
from pytest_ansible.logger import get_logger
from pytest_ansible.fixtures import (ansible_adhoc, ansible_module, ansible_facts, localhost)
from pytest_ansible.host_manager import get_host_manager

import ansible
import ansible.constants
import ansible.utils
import ansible.errors
from ansible.inventory import Inventory

has_ansible_v2 = parse_version(ansible.__version__) >= parse_version('2.0.0')

log = get_logger(__name__)

# Silence linters for imported fixtures
(ansible_adhoc, ansible_module, ansible_facts, localhost)


def pytest_addoption(parser):
    """Add options to control ansible."""
    log.debug("pytest_addoption() called")

    group = parser.getgroup('pytest-ansible')
    group.addoption('--ansible-inventory', '--inventory',
                    action='store',
                    dest='ansible_inventory',
                    default=ansible.constants.DEFAULT_HOST_LIST,
                    metavar='ANSIBLE_INVENTORY',
                    help='ansible inventory file URI (default: %(default)s)')
    group.addoption('--ansible-host-pattern', '--host-pattern',
                    action='store',
                    dest='ansible_host_pattern',
                    default=None,
                    metavar='ANSIBLE_HOST_PATTERN',
                    help='ansible host pattern (default: %(default)s)')
    group.addoption('--ansible-limit', '--limit',
                    action='store',
                    dest='ansible_subset',
                    default=ansible.constants.DEFAULT_SUBSET,
                    metavar='ANSIBLE_SUBSET',
                    help='further limit selected hosts to an additional pattern')
    group.addoption('--ansible-connection', '--connection',
                    action='store',
                    dest='ansible_connection',
                    default=ansible.constants.DEFAULT_TRANSPORT,
                    help="connection type to use (default: %(default)s)")
    group.addoption('--ansible-user', '--user',
                    action='store',
                    dest='ansible_user',
                    default=ansible.constants.DEFAULT_REMOTE_USER,
                    help='connect as this user (default: %(default)s)')
    group.addoption('--ansible-check', '--check',
                    action='store_true',
                    dest='ansible_check',
                    default=False,
                    help='don\'t make any changes; instead, try to predict some of the changes that may occur')
    group.addoption('--ansible-module-path', '--module-path',
                    action='store',
                    dest='ansible_module_path',
                    default=ansible.constants.DEFAULT_MODULE_PATH,
                    help='specify path(s) to module library (default: %(default)s)')

    # become privilege escalation
    group.addoption('--ansible-become', '--become',
                    action='store_true',
                    dest='ansible_become',
                    default=ansible.constants.DEFAULT_BECOME,
                    help='run operations with become, nopasswd implied (default: %(default)s)')
    group.addoption('--ansible-become-method', '--become-method',
                    action='store',
                    dest='ansible_become_method',
                    default=ansible.constants.DEFAULT_BECOME_METHOD,
                    help="privilege escalation method to use (default: %%(default)s), valid choices: [ %s ]" % (' | '.join(ansible.constants.BECOME_METHODS)))
    group.addoption('--ansible-become-user', '--become-user',
                    action='store',
                    dest='ansible_become_user',
                    default=ansible.constants.DEFAULT_BECOME_USER,
                    help='run operations as this user (default: %(default)s)')
    group.addoption('--ansible-ask-become-pass', '--ask-become-pass',
                    action='store',
                    dest='ansible_ask_become_pass',
                    default=ansible.constants.DEFAULT_BECOME_ASK_PASS,
                    help='ask for privilege escalation password (default: %(default)s)')

    # Add github marker to --help
    parser.addini("ansible", "Ansible integration", "args")


def pytest_configure(config):
    '''
    Validate --ansible-* parameters.
    '''
    log.debug("pytest_configure() called")

    config.addinivalue_line("markers", "ansible(**kwargs): Ansible integration")

    # Enable connection debugging
    if config.option.verbose > 0:
        if has_ansible_v2:
            from ansible.utils.display import Display
            display = Display()
            display.verbosity = int(config.option.verbose)
        else:
            ansible.utils.VERBOSITY = int(config.option.verbose)

    assert config.pluginmanager.register(PyTestAnsiblePlugin(config), "ansible")


def pytest_generate_tests(metafunc):
    log.debug("pytest_generate_tests() called")

    if 'ansible_host' in metafunc.fixturenames:
        # assert required --ansible-* parameters were used
        PyTestAnsiblePlugin.assert_required_ansible_parameters(metafunc.config)
        # TODO: figure out how to use PyTestAnsiblePlugin.initialize() instead
        try:
            inventory_manager = Inventory(metafunc.config.getoption('ansible_inventory'))
        except ansible.errors.AnsibleError, e:
            raise pytest.UsageError(e)
        pattern = metafunc.config.getoption('ansible_host_pattern')
        metafunc.parametrize("ansible_host", inventory_manager.list_hosts(pattern))
    if 'ansible_group' in metafunc.fixturenames:
        # assert required --ansible-* parameters were used
        PyTestAnsiblePlugin.assert_required_ansible_parameters(metafunc.config)
        # TODO: figure out how to use PyTestAnsiblePlugin.initialize() instead
        try:
            inventory_manager = Inventory(metafunc.config.getoption('ansible_inventory'))
        except ansible.errors.AnsibleError, e:
            raise pytest.UsageError(e)
        metafunc.parametrize("ansible_group", inventory_manager.list_groups())


class PyTestAnsiblePlugin:

    def __init__(self, config):
        log.debug("PyTestAnsiblePlugin initialized")
        self.config = config

    def pytest_report_header(self, config, startdir):
        log.debug("pytest_report_header() called")

        return 'ansible: %s' % ansible.__version__

    def pytest_collection_modifyitems(self, session, config, items):
        '''
        Validate --ansible-* parameters.
        '''
        log.debug("pytest_collection_modifyitems() called")

        uses_ansible_fixtures = False
        for item in items:
            if not hasattr(item, 'fixturenames'):
                continue
            if any([fixture.startswith('ansible_') for fixture in item.fixturenames]):
                # TODO - ignore if they are using a marker
                # marker = item.get_marker('ansible')
                # if marker and 'inventory' in marker.kwargs:
                uses_ansible_fixtures = True
                break

        if uses_ansible_fixtures:
            # assert required --ansible-* parameters were used
            self.assert_required_ansible_parameters(config)

    def _load_ansible_config(self, request):
        '''Load ansible configuration from command-line and decorator kwargs.'''

        # List of config parameter names
        option_names = ['ansible_inventory', 'ansible_host_pattern', 'ansible_connection', 'ansible_user',
                        'ansible_module_path', 'ansible_become', 'ansible_become_method', 'ansible_become_user',
                        'ansible_ask_become_pass', 'ansible_subset']

        # Remember the pytest request attr
        kwargs = dict(__request__=request)

        # Load command-line supplied values
        for key in option_names:
            short_key = key[8:]
            kwargs[short_key] = request.config.getoption(key)

        # Override options from @pytest.mark.ansible
        marker_kwargs = self._get_marker_kwargs(request)

        # Merge marker_kwargs with kwargs
        if marker_kwargs:
            for short_key in kwargs.keys():
                if short_key in marker_kwargs:
                    kwargs[short_key] = marker_kwargs[short_key]
                    log.debug("ansible marker override %s:%s" % (short_key, kwargs[short_key]))

        # Was this fixture called in conjunction with a parametrized fixture
        if 'ansible_host' in request.fixturenames:
            kwargs['host_pattern'] = request.getfuncargvalue('ansible_host')
        elif 'ansible_group' in request.fixturenames:
            kwargs['host_pattern'] = request.getfuncargvalue('ansible_group')

        # normalize ansible.ansible_become options
        kwargs['become'] = kwargs['become'] or ansible.constants.DEFAULT_BECOME
        kwargs['become_user'] = kwargs['become_user'] or ansible.constants.DEFAULT_BECOME_USER
        kwargs['ask_become_pass'] = kwargs['ask_become_pass'] or ansible.constants.DEFAULT_BECOME_ASK_PASS

        log.debug("kwargs: %s" % kwargs)
        return kwargs

    def _get_marker_kwargs(self, request):
        '''Returns a dictionary of the ansible parameters supplied to the ansible marker.'''

        if request.scope == 'function':
            if hasattr(request.function, 'ansible'):
                return request.function.ansible.kwargs
        elif request.scope == 'class':
            if hasattr(request.cls, 'pytestmark'):
                for pytestmark in request.cls.pytestmark:
                    if pytestmark.name == 'ansible':
                        return pytestmark.kwargs
                    else:
                        continue
        return {}

    def initialize(self, request, **kwargs):
        '''Returns an initialized Ansible Host Manager instance
        '''
        ansible_cfg = self._load_ansible_config(request)
        ansible_cfg.update(kwargs)
        return get_host_manager(**ansible_cfg)

    @staticmethod
    def assert_required_ansible_parameters(config):
        '''Helper method to assert whether the required --ansible-* parameters were
        provided.
        '''

        errors = []

        # Verify --ansible-host-pattern was provided
        ansible_hostname = config.getoption('ansible_host_pattern')
        if ansible_hostname is None or ansible_hostname == '':
            errors.append("Missing required parameter --ansible-host-pattern/--host-pattern")

        # NOTE: I don't think this will ever catch issues since ansible_inventory
        # defaults to '/etc/ansible/hosts'
        # Verify --ansible-inventory was provided
        ansible_inventory = config.getoption('ansible_inventory')
        if ansible_inventory is None or ansible_inventory == "":
            errors.append("Unable to find an inventory file, specify one with the --ansible-inventory/--inventory "
                          "parameter.")

        if errors:
            raise pytest.UsageError(*errors)
