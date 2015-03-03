import os
import pytest
import logging
import ansible.runner
import ansible.constants
import ansible.inventory
import ansible.utils
from pytest_ansible.errors import AnsibleNoHostsMatch, AnsibleHostUnreachable


log = logging.getLogger(__name__)
# ansible.utils.VERBOSITY = 4


def pytest_addoption(parser):
    '''Add options to control ansible.'''

    def increment_debug(option, opt, value, parser):
        ansible.utils.VERBOSITY += 1

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
    group.addoption('--ansible-sudo',
                    action='store_true',
                    dest='ansible_sudo',
                    default=ansible.constants.DEFAULT_SUDO,
                    help='run operations with sudo [nopasswd] (default: %default)')
    group.addoption('--ansible-sudo-user',
                    action='store',
                    dest='ansible_sudo_user',
                    default='root',
                    help='desired sudo user (default: %default)')


def pytest_configure(config):
    '''
    Sanitize --ansible-* parameters.
    Ensure --ansible-inventory references a valid file. If a remote URL is
    used, download the file locally.
    '''

    # Sanitize ansible_hostname
    ansible_hostname = config.getvalue('ansible_host_pattern')

    # Verify --ansible-host-pattern was provided
    if not (config.option.help or config.option.showfixtures):
        if ansible_hostname is None or ansible_hostname == '':
            msg = "ERROR: Missing required parameter --ansible-host-pattern"
            print(msg)
            pytest.exit(msg)

    # Verify --ansible-inventory was provided
    ansible_inventory = config.getvalue('ansible_inventory')
    if not config.option.collectonly:
        '''
        Do some validation with the host_pattern?
        '''
        if not os.path.exists(ansible_inventory):
            msg = "ERROR: Unable to find an inventory file, specify one with --ansible-inventory ?"
            print(msg)
            pytest.exit(msg)


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
        self.inventory_manager = ansible.inventory.Inventory(self.inventory)
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
        runner = ansible.runner.Runner(
            inventory=self.inventory_manager,
            pattern=self.pattern,
            module_name=self.module_name,
            module_args=module_args,
            complex_args=kwargs,
            transport=self.options.get('connection'),
            sudo=self.options.get('sudo'),
            sudo_user=self.options.get('sudo_user'),)

        # Run the module
        results = runner.run()

        # FIXME - improve result output logging
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
    kwfields = ('ansible_inventory', 'ansible_host_pattern',
                'ansible_connection', 'ansible_user', 'ansible_sudo', 'ansible_sudo_user')
    for key in kwfields:
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
        for key in kwfields:
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
        # this doesn't support function/cls fixture overrides
        inventory_manager = ansible.inventory.Inventory(metafunc.config.getvalue('ansible_inventory'))
        pattern = metafunc.config.getvalue('ansible_host_pattern')
        metafunc.parametrize("ansible_host", inventory_manager.list_hosts(pattern))
    if 'ansible_group' in metafunc.fixturenames:
        inventory_manager = ansible.inventory.Inventory(metafunc.config.getvalue('ansible_inventory'))
        metafunc.parametrize("ansible_group", inventory_manager.list_groups())
