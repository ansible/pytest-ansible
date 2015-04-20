import os
import pytest
import logging
import ansible
import ansible.runner
import ansible.constants
import ansible.inventory
import ansible.utils
import ansible.errors
from pytest_ansible.errors import AnsibleNoHostsMatch, AnsibleHostUnreachable
from pkg_resources import parse_version


has_ansible_become = parse_version(ansible.__version__) >= parse_version('1.9.0')


log = logging.getLogger(__name__)


def pytest_addoption(parser):
    '''Add options to control ansible.'''

    group = parser.getgroup('pytest-ansible')
    group.addoption('--ansible-inventory',
                    action='store',
                    dest='ansible_inventory',
                    default=ansible.constants.DEFAULT_HOST_LIST,
                    metavar='ANSIBLE_INVENTORY',
                    help='ansible inventory file URI (default: %default)')
    group.addoption('--ansible-host-pattern',
                    action='store',
                    dest='ansible_host_pattern',
                    default=None,
                    metavar='ANSIBLE_HOST_PATTERN',
                    help='ansible host pattern (default: %default)')
    group.addoption('--ansible-connection',
                    action='store',
                    dest='ansible_connection',
                    default=ansible.constants.DEFAULT_TRANSPORT,
                    help="connection type to use (default: %default)")
    group.addoption('--ansible-user',
                    action='store',
                    dest='ansible_user',
                    default=ansible.constants.DEFAULT_REMOTE_USER,
                    help='connect as this user (default: %default)')
    group.addoption('--ansible-debug',
                    action='store_true',
                    dest='ansible_debug',
                    default=False,
                    help='enable ansible connection debugging')

    # classic privilege escalation
    group.addoption('--ansible-sudo',
                    action='store_true',
                    dest='ansible_sudo',
                    default=ansible.constants.DEFAULT_SUDO,
                    help='run operations with sudo [nopasswd] (default: %default) (deprecated, use become)')
    group.addoption('--ansible-sudo-user',
                    action='store',
                    dest='ansible_sudo_user',
                    default='root',
                    help='desired sudo user (default: %default) (deprecated, use become)')

    if has_ansible_become:
        # consolidated privilege escalation
        group.addoption('--ansible-become',
                        action='store_true',
                        dest='ansible_become',
                        default=ansible.constants.DEFAULT_BECOME,
                        help='run operations with become, nopasswd implied (default: %default)')
        group.addoption('--ansible-become-method',
                        action='store',
                        dest='ansible_become_method',
                        default=ansible.constants.DEFAULT_BECOME_METHOD,
                        help="privilege escalation method to use (default: %%default), valid choices: [ %s ]" % (' | '.join(ansible.constants.BECOME_METHODS)))
        group.addoption('--ansible-become-user',
                        action='store',
                        dest='ansible_become_user',
                        default=ansible.constants.DEFAULT_BECOME_USER,
                        help='run operations as this user (default: %default)')


def assert_required_ansible_parameters(config):
    '''Helper method to assert whether the required --ansible-* parameters were
    provided.
    '''

    errors = []

    # Verify --ansible-host-pattern was provided
    ansible_hostname = config.getvalue('ansible_host_pattern')
    if ansible_hostname is None or ansible_hostname == '':
        errors.append("Missing required parameter --ansible-host-pattern")

    # NOTE: I don't think this will ever catch issues since ansible_inventory
    # defaults to '/etc/ansible/hosts'
    # Verify --ansible-inventory was provided
    ansible_inventory = config.getvalue('ansible_inventory')
    if ansible_inventory is None or ansible_inventory == "":
        errors.append("Unable to find an inventory file, specify one with the --ansible-inventory parameter.")

    if errors:
        raise pytest.UsageError(*errors)


def pytest_collection_modifyitems(session, config, items):
    '''
    Validate --ansible-* parameters.
    '''

    uses_ansible_fixtures = False
    for item in items:
        if not hasattr(item, 'fixturenames'):
            continue
        if any([fixture.startswith('ansible_') for fixture in item.fixturenames]):
            # TODO - ignore if they are using a marker
            marker = item.get_marker('ansible')
            # if marker and 'inventory' in marker.kwargs:
            uses_ansible_fixtures = True
            break

    if uses_ansible_fixtures:
        # assert required --ansible-* parameters were used
        assert_required_ansible_parameters(config)


def pytest_configure(config):
    '''
    Validate --ansible-* parameters.
    '''

    # Enable connection debugging
    if config.getvalue('ansible_debug'):
        ansible.utils.VERBOSITY = 5


#def pytest_collection_modifyitems(session, config, items):
#    reporter = config.pluginmanager.getplugin("terminalreporter")
#    reporter.write("ansible: %s\n" % ansible.__version__)


class AnsibleModule(object):
    '''
    Wrapper around ansible.runner.Runner()

    Sample Usage:
      ansible = AnsibleModule(inventory='/path/to/inventory')
      results = ansible.command('mkdir /var/lib/testing', creates='/var/lib/testing')
      results = ansible.git(repo='https://github.com/ansible/ansible.git', dest='/tmp/ansible')
    '''

    def __init__(self, **kwargs):
        log.debug("AnsibleWrapper(%s)" % kwargs)

        self.options = kwargs

        # Module name is used when accessing an instance attribute (e.g.
        # self.ping)
        self.module_name = None

        # Initialize ansible inventory manage
        self.inventory_manager = None

        assert 'inventory' in self.options, "Missing required keyword argument 'inventory'"
        self.inventory = self.options.get('inventory')
        assert 'host_pattern' in self.options, "Missing required keyword argument 'host_pattern'"
        self.pattern = self.options.get('host_pattern')

        # Initialize inventory_manager with the provided inventory and host_pattern
        try:
            self.inventory_manager = ansible.inventory.Inventory(self.inventory)
        except ansible.errors.AnsibleError, e:
            # raise
            # pytest.fail(e)
            raise pytest.UsageError(e)
        self.inventory_manager.subset(self.pattern)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            self.module_name = name
            return self.__run

    def __run(self, *args, **kwargs):
        '''
        The API provided by ansible is not intended as a public API.
        '''

        # Assemble module argument string
        module_args = list()
        if args:
            module_args += list(args)
        module_args = ' '.join(module_args)

        # Assert hosts matching the provided pattern exist
        hosts = self.inventory_manager.list_hosts(self.pattern)
        if len(hosts) == 0:
            raise AnsibleNoHostsMatch("No hosts match:'%s'" % self.pattern)

        # Log the module and parameters
        log.debug("[%s] %s: %s, %s" % (self.pattern, self.module_name, module_args, kwargs))

        # Build module runner object
        kwargs = dict(
            inventory=self.inventory_manager,
            pattern=self.pattern,
            module_name=self.module_name,
            module_args=module_args,
            complex_args=kwargs,
            transport=self.options.get('connection'),
            remote_user=self.options.get('user'),
        )

        # Handle >= 1.9.0 options
        if has_ansible_become:
            kwargs.update(dict(
                become=self.options.get('become'),
                become_method=self.options.get('become_method'),
                become_user=self.options.get('become_user'),)
            )
        else:
            kwargs.update(dict(
                sudo=self.options.get('sudo'),
                sudo_user=self.options.get('sudo_user'),)
            )

        runner = ansible.runner.Runner(**kwargs)

        # Run the module
        results = runner.run()

        # Log the results
        log.debug(results)

        # FIXME - should command failures raise an exception, or return?
        # If we choose to raise, callers will need to adapt accordingly
        # Catch any failures in the response
        # for host in results['contacted'].values():
        #     if 'failed' in host or host.get('rc', 0) != 0:
        #         raise Exception("Command failed: %s" % self.module_name, results)

        # Raise exception if host(s) unreachable
        # FIXME - if multiple hosts were involved, should an exception be raised?
        if results['dark']:
            print results['dark']
            raise AnsibleHostUnreachable("Host unreachable", dark=results['dark'], contacted=results['contacted'])

        # No hosts contacted
        # if not results['contacted']:
        #     raise ansible.errors.AnsibleConnectionFailed("Provided hosts list is empty")

        # Success!
        # return results
        return results['contacted']


def initialize(request):
    '''Returns an initialized AnsibleModule instance
    '''

    # Remember the pytest request attr
    kwargs = dict(__request__=request)

    # Grab options from command-line
    option_names = ['ansible_inventory', 'ansible_host_pattern',
                    'ansible_connection', 'ansible_user', 'ansible_sudo',
                    'ansible_sudo_user']

    # Grab ansible-1.9 become options
    if has_ansible_become:
        option_names.extend(['ansible_become', 'ansible_become_method',
            'ansible_become_user'])

    for key in option_names:
        short_key = key[8:]
        kwargs[short_key] = request.config.getvalue(key)

    # Override options from @pytest.mark.ansible
    ansible_args = dict()
    if request.scope == 'function':
        if hasattr(request.function, 'ansible'):
            ansible_args = request.function.ansible.kwargs
    elif request.scope == 'class':
        if hasattr(request.cls, 'pytestmark'):
            for pytestmark in request.cls.pytestmark:
                if pytestmark.name == 'ansible':
                    ansible_args = pytestmark.kwargs
                else:
                    continue

    # Build kwargs to pass along to AnsibleModule
    if ansible_args:
        for key in option_names:
            short_key = key[8:]
            if short_key not in ansible_args:
                continue
            kwargs[short_key] = ansible_args[short_key]
            log.debug("Override %s:%s" % (short_key, kwargs[short_key]))

    # Was this fixture called in conjunction with a parametrized fixture
    if 'ansible_host' in request.fixturenames:
        kwargs['host_pattern'] = request.getfuncargvalue('ansible_host')
    elif 'ansible_group' in request.fixturenames:
        kwargs['host_pattern'] = request.getfuncargvalue('ansible_group')

    if has_ansible_become:
        # normalize ansible.ansible_become options
        kwargs['become'] = kwargs['become'] or kwargs['sudo'] or \
            ansible.constants.DEFAULT_BECOME
        kwargs['become_user'] = kwargs['become_user'] or kwargs['sudo_user'] or \
            ansible.constants.DEFAULT_BECOME_USER
        #kwargs['become_ask_pass'] = kwargs.get('become_ask_pass', kwargs.get('ask_sudo_pass', kwargs.get('ask_su_pass', ansible.constants.DEFAULT_BECOME_ASK_PASS)))

    return AnsibleModule(**kwargs)


@pytest.fixture(scope='class')
def ansible_module_cls(request):
    '''
    Return AnsibleModule instance with class scope.
    '''

    return initialize(request)


@pytest.fixture(scope='function')
def ansible_module(request):
    '''
    Return AnsibleModule instance with function scope.
    '''

    return initialize(request)


@pytest.fixture(scope='function')
def ansible_facts_cls(ansible_module_cls):
    '''
    Return ansible_facts dictionary
    '''
    try:
        return ansible_module_cls.setup()
    except AnsibleHostUnreachable, e:
        log.warning("Hosts unreachable: %s" % e.dark.keys())
        return e.contacted


@pytest.fixture(scope='function')
def ansible_facts(ansible_module):
    '''
    Return ansible_facts dictionary
    '''
    try:
        return ansible_module.setup()
    except AnsibleHostUnreachable, e:
        log.warning("Hosts unreachable: %s" % e.dark.keys())
        return e.contacted


def pytest_generate_tests(metafunc):
    if 'ansible_host' in metafunc.fixturenames:
        # assert required --ansible-* parameters were used
        assert_required_ansible_parameters(metafunc.config)
        # TODO: this doesn't support function/cls fixture overrides
        try:
            inventory_manager = ansible.inventory.Inventory(metafunc.config.getvalue('ansible_inventory'))
        except ansible.errors.AnsibleError, e:
            raise pytest.UsageError(e)
        pattern = metafunc.config.getvalue('ansible_host_pattern')
        metafunc.parametrize("ansible_host", inventory_manager.list_hosts(pattern))
    if 'ansible_group' in metafunc.fixturenames:
        # assert required --ansible-* parameters were used
        assert_required_ansible_parameters(metafunc.config)
        try:
            inventory_manager = ansible.inventory.Inventory(metafunc.config.getvalue('ansible_inventory'))
        except ansible.errors.AnsibleError, e:
            raise pytest.UsageError(e)
        metafunc.parametrize("ansible_group", inventory_manager.list_groups())


def pytest_report_header(config):
    '''Include the version of ansible in the report header
    '''
    return 'ansible: %s' % ansible.__version__
