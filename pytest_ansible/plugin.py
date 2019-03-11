"""PyTest Ansible Plugin."""

import pytest
import ansible
import ansible.constants
import ansible.utils
import ansible.errors

try:
    from ansible.plugins import become_loader
except ImportError:
    become_loader = None

from pytest_ansible.logger import get_logger
from pytest_ansible.fixtures import (ansible_adhoc, ansible_module, ansible_facts, localhost)
from pytest_ansible.host_manager import get_host_manager

log = get_logger(__name__)

# Silence linters for imported fixtures
(ansible_adhoc, ansible_module, ansible_facts, localhost)


def become_methods():
    """Return string list of become methods available to ansible."""
    if become_loader:
        return [method.name for method in become_loader.all()]
    else:
        return ansible.constants.BECOME_METHODS


def pytest_addoption(parser):
    """Add options to control ansible."""
    log.debug("pytest_addoption() called")

    group = parser.getgroup('pytest-ansible')
    group.addoption('--inventory', '--ansible-inventory',
                    action='store',
                    dest='ansible_inventory',
                    default=ansible.constants.DEFAULT_HOST_LIST,
                    metavar='ANSIBLE_INVENTORY',
                    help='ansible inventory file URI (default: %(default)s)')
    group.addoption('--host-pattern', '--ansible-host-pattern',
                    action='store',
                    dest='ansible_host_pattern',
                    default=None,
                    metavar='ANSIBLE_HOST_PATTERN',
                    help='ansible host pattern (default: %(default)s)')
    group.addoption('--limit', '--ansible-limit',
                    action='store',
                    dest='ansible_subset',
                    default=ansible.constants.DEFAULT_SUBSET,
                    metavar='ANSIBLE_SUBSET',
                    help='further limit selected hosts to an additional pattern')
    group.addoption('--connection', '--ansible-connection',
                    action='store',
                    dest='ansible_connection',
                    default=ansible.constants.DEFAULT_TRANSPORT,
                    help="connection type to use (default: %(default)s)")
    group.addoption('--user', '--ansible-user',
                    action='store',
                    dest='ansible_user',
                    default=ansible.constants.DEFAULT_REMOTE_USER,
                    help='connect as this user (default: %(default)s)')
    group.addoption('--check', '--ansible-check',
                    action='store_true',
                    dest='ansible_check',
                    default=False,
                    help='don\'t make any changes; instead, try to predict some of the changes that may occur')
    group.addoption('--module-path', '--ansible-module-path',
                    action='store',
                    dest='ansible_module_path',
                    default=ansible.constants.DEFAULT_MODULE_PATH,
                    help='specify path(s) to module library (default: %(default)s)')

    # become privilege escalation
    group.addoption('--become', '--ansible-become',
                    action='store_true',
                    dest='ansible_become',
                    default=ansible.constants.DEFAULT_BECOME,
                    help='run operations with become, nopasswd implied (default: %(default)s)')
    group.addoption('--become-method', '--ansible-become-method',
                    action='store',
                    dest='ansible_become_method',
                    default=ansible.constants.DEFAULT_BECOME_METHOD,
                    help="privilege escalation method to use (default: %%(default)s), valid choices: [ %s ]" %
                    (' | '.join(become_methods())))
    group.addoption('--become-user', '--ansible-become-user',
                    action='store',
                    dest='ansible_become_user',
                    default=ansible.constants.DEFAULT_BECOME_USER,
                    help='run operations as this user (default: %(default)s)')
    group.addoption('--ask-become-pass', '--ansible-ask-become-pass',
                    action='store',
                    dest='ansible_ask_become_pass',
                    default=ansible.constants.DEFAULT_BECOME_ASK_PASS,
                    help='ask for privilege escalation password (default: %(default)s)')

    # Add github marker to --help
    parser.addini("ansible", "Ansible integration", "args")


def pytest_configure(config):
    """Validate --ansible-* parameters."""
    log.debug("pytest_configure() called")

    config.addinivalue_line("markers", "ansible(**kwargs): Ansible integration")

    # Enable connection debugging
    if config.option.verbose > 0:
        if hasattr(ansible.utils, 'VERBOSITY'):
            ansible.utils.VERBOSITY = int(config.option.verbose)
        else:
            from ansible.utils.display import Display
            display = Display()
            display.verbosity = int(config.option.verbose)

    assert config.pluginmanager.register(PyTestAnsiblePlugin(config), "ansible")


def pytest_generate_tests(metafunc):
    """Generate tests when specific `ansible_*` fixtures are used by tests."""
    log.debug("pytest_generate_tests() called")

    if 'ansible_host' in metafunc.fixturenames:
        # assert required --ansible-* parameters were used
        PyTestAnsiblePlugin.assert_required_ansible_parameters(metafunc.config)
        try:
            plugin = metafunc.config.pluginmanager.getplugin("ansible")
            hosts = plugin.initialize(config=plugin.config, pattern=metafunc.config.getoption('ansible_host_pattern'))
        except ansible.errors.AnsibleError as e:
            raise pytest.UsageError(e)
        # Return the host name as a string
        # metafunc.parametrize("ansible_host", hosts.keys())
        # Return a HostManager instance where pattern=host (e.g. ansible_host.all.shell('date'))
        # metafunc.parametrize("ansible_host", iter(plugin.initialize(config=plugin.config, pattern=h) for h in
        #                                           hosts.keys()))
        # Return a ModuleDispatcher instance representing `host` (e.g. ansible_host.shell('date'))
        metafunc.parametrize("ansible_host", iter(hosts[h] for h in hosts.keys()))

    if 'ansible_group' in metafunc.fixturenames:
        # assert required --ansible-* parameters were used
        PyTestAnsiblePlugin.assert_required_ansible_parameters(metafunc.config)
        try:
            plugin = metafunc.config.pluginmanager.getplugin("ansible")
            hosts = plugin.initialize(config=plugin.config, pattern=metafunc.config.getoption('ansible_host_pattern'))
        except ansible.errors.AnsibleError as e:
            raise pytest.UsageError(e)
        # FIXME: Eeew, this shouldn't be interfacing with `hosts.options`
        groups = hosts.options['inventory_manager'].list_groups()
        # Return the group name as a string
        # metafunc.parametrize("ansible_group", groups)
        # Return a ModuleDispatcher instance representing the group (e.g. ansible_group.shell('date'))
        metafunc.parametrize("ansible_group", iter(hosts[g] for g in groups))


class PyTestAnsiblePlugin:

    """Ansible PyTest Plugin Class."""

    def __init__(self, config):
        """Initialize plugin."""
        log.debug("PyTestAnsiblePlugin initialized")
        self.config = config

    def pytest_report_header(self, config, startdir):
        """Return the version of ansible."""
        log.debug("pytest_report_header() called")
        return 'ansible: %s' % ansible.__version__

    def pytest_collection_modifyitems(self, session, config, items):
        """Validate --ansible-* parameters."""
        log.debug("pytest_collection_modifyitems() called")
        log.debug("items: %s" % items)

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

    def _load_ansible_config(self, config):
        """Load ansible configuration from command-line."""
        option_names = ['ansible_inventory', 'ansible_host_pattern', 'ansible_connection', 'ansible_user',
                        'ansible_module_path', 'ansible_become', 'ansible_become_method', 'ansible_become_user',
                        'ansible_ask_become_pass', 'ansible_subset']

        kwargs = dict()

        # Load command-line supplied values
        for key in option_names:
            short_key = key[8:]
            kwargs[short_key] = config.getoption(key)

        # normalize ansible.ansible_become options
        kwargs['become'] = kwargs['become'] or ansible.constants.DEFAULT_BECOME
        kwargs['become_user'] = kwargs['become_user'] or ansible.constants.DEFAULT_BECOME_USER
        kwargs['ask_become_pass'] = kwargs['ask_become_pass'] or ansible.constants.DEFAULT_BECOME_ASK_PASS

        log.debug("config: %s" % kwargs)
        return kwargs

    def _load_request_config(self, request):
        """Load ansible configuration from decorator kwargs."""
        kwargs = dict()

        # Override options from @pytest.mark.ansible
        marker = request.node.get_closest_marker('ansible')
        if marker:
            kwargs = marker.kwargs

        log.debug("request: %s" % kwargs)
        return kwargs

    def initialize(self, config=None, request=None, **kwargs):
        """Return an initialized Ansible Host Manager instance."""
        ansible_cfg = dict()
        # merge command-line configuration options
        if config is not None:
            ansible_cfg.update(self._load_ansible_config(config))
        # merge pytest request configuration options
        if request is not None:
            ansible_cfg.update(self._load_request_config(request))
        # merge in provided kwargs
        ansible_cfg.update(kwargs)
        return get_host_manager(**ansible_cfg)

    @staticmethod
    def assert_required_ansible_parameters(config):
        """Assert whether the required --ansible-* parameters were provided."""
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
