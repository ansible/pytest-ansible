import pytest
import logging
from pkg_resources import parse_version
from .fixtures import (ansible_module_cls, ansible_module, ansible_facts_cls, ansible_facts)
from .errors import AnsibleNoHostsMatch, AnsibleHostUnreachable

# conditionally import ansible libraries
import ansible
import ansible.constants
import ansible.utils
import ansible.errors
has_ansible_become = parse_version(ansible.__version__) >= parse_version('1.9.0')
has_ansible_v2 = parse_version(ansible.__version__) >= parse_version('2.0.0')

if has_ansible_v2:
    from ansible.plugins.callback import CallbackBase
    from ansible.executor.task_queue_manager import TaskQueueManager
    from ansible.parsing.dataloader import DataLoader
    from ansible.playbook.play import Play
    from ansible.vars import VariableManager
    from ansible.cli import CLI
    from ansible.inventory import Inventory
    from ansible.utils.display import Display
    display = Display()
else:
    from ansible.runner import Runner
    from ansible.inventory import Inventory

try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):

        def emit(self, record):
            pass
log = logging.getLogger(__name__)
log.addHandler(NullHandler())

# Silence linters for imported fixtures
(ansible_module_cls, ansible_module, ansible_facts_cls, ansible_facts)


def pytest_addoption(parser):
    '''Add options to control ansible.'''
    log.debug("pytest_addoption() called")

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
                    default=ansible.constants.DEFAULT_DEBUG,
                    help='enable ansible connection debugging')
    group.addoption('--ansible-module-path',
                    action='store',
                    dest='ansible_module_path',
                    default=ansible.constants.DEFAULT_MODULE_PATH,
                    help='specify path(s) to module library (default: %default)')

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

    # Add github marker to --help
    parser.addini("ansible", "Ansible integration", "args")


def pytest_configure(config):
    '''
    Validate --ansible-* parameters.
    '''
    log.debug("pytest_configure() called")

    config.addinivalue_line("markers", "ansible(**kwargs): Ansible integration")

    # Enable connection debugging
    if config.getvalue('ansible_debug'):
        if has_ansible_v2:
            display.verbosity = 5
        else:
            ansible.utils.VERBOSITY = 5

    assert config.pluginmanager.register(PyTestAnsiblePlugin(config), "ansible")


class PyTestAnsiblePlugin:

    def __init__(self, config):
        log.debug("PyTestAnsiblePlugin initialized")
        self.config = config

    def assert_required_ansible_parameters(self):
        '''Helper method to assert whether the required --ansible-* parameters were
        provided.
        '''

        errors = []

        # Verify --ansible-host-pattern was provided
        ansible_hostname = self.config.getvalue('ansible_host_pattern')
        if ansible_hostname is None or ansible_hostname == '':
            errors.append("Missing required parameter --ansible-host-pattern")

        # NOTE: I don't think this will ever catch issues since ansible_inventory
        # defaults to '/etc/ansible/hosts'
        # Verify --ansible-inventory was provided
        ansible_inventory = self.config.getvalue('ansible_inventory')
        if ansible_inventory is None or ansible_inventory == "":
            errors.append("Unable to find an inventory file, specify one with the --ansible-inventory parameter.")

        if errors:
            raise pytest.UsageError(*errors)

    def pytest_generate_tests(self, metafunc):
        log.debug("pytest_generate_tests() called")

        if 'ansible_host' in metafunc.fixturenames:
            # assert required --ansible-* parameters were used
            self.assert_required_ansible_parameters()
            # TODO: this doesn't support function/cls fixture overrides
            try:
                inventory_manager = Inventory(self.config.getvalue('ansible_inventory'))
            except ansible.errors.AnsibleError, e:
                raise pytest.UsageError(e)
            pattern = self.config.getvalue('ansible_host_pattern')
            metafunc.parametrize("ansible_host", inventory_manager.list_hosts(pattern))
        if 'ansible_group' in metafunc.fixturenames:
            # assert required --ansible-* parameters were used
            self.assert_required_ansible_parameters()
            try:
                inventory_manager = Inventory(self.config.getvalue('ansible_inventory'))
            except ansible.errors.AnsibleError, e:
                raise pytest.UsageError(e)
            metafunc.parametrize("ansible_group", inventory_manager.list_groups())

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
            self.assert_required_ansible_parameters()

    # def pytest_collection_modifyitems(session, config, items):
    #     reporter = config.pluginmanager.getplugin("terminalreporter")
    #     reporter.write("ansible: %s\n" % ansible.__version__)

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

    def initialize(self, request):
        '''Returns an initialized Ansible Module Wrapper instance
        '''

        # List of config parameter names
        option_names = ['ansible_inventory', 'ansible_host_pattern',
                        'ansible_connection', 'ansible_user', 'ansible_sudo',
                        'ansible_sudo_user', 'ansible_module_path']

        # Add ansible-1.9 become options
        if has_ansible_become:
            option_names.extend(['ansible_become', 'ansible_become_method', 'ansible_become_user'])

        # Remember the pytest request attr
        kwargs = dict(__request__=request)

        # Load command-line supplied values
        for key in option_names:
            short_key = key[8:]
            kwargs[short_key] = request.config.getvalue(key)

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
        if has_ansible_become:
            # normalize ansible.ansible_become options
            kwargs['become'] = kwargs['become'] or kwargs['sudo'] or \
                ansible.constants.DEFAULT_BECOME
            kwargs['become_user'] = kwargs['become_user'] or kwargs['sudo_user'] or \
                ansible.constants.DEFAULT_BECOME_USER
            # kwargs['become_ask_pass'] = kwargs.get('become_ask_pass', kwargs.get('ask_sudo_pass', kwargs.get('ask_su_pass', ansible.constants.DEFAULT_BECOME_ASK_PASS)))  # NOQA

        log.debug("kwargs: %s" % kwargs)
        if has_ansible_v2:
            return AnsibleV2Module(**kwargs)
        else:
            return AnsibleV1Module(**kwargs)


class AnsibleV1Module(object):

    '''
    Wrapper around ansible.runner.Runner()

    Sample Usage:
      ansible = AnsibleV1Module(inventory='/path/to/inventory')
      results = ansible.command('mkdir /var/lib/testing', creates='/var/lib/testing')
      results = ansible.git(repo='https://github.com/ansible/ansible.git', dest='/tmp/ansible')
    '''

    def __init__(self, **kwargs):
        log.debug("AnsibleWrapper(%s)" % kwargs)

        self.options = kwargs

        # Module name is used when accessing an instance attribute (e.g.
        # self.ping)
        self.module_name = None

        assert 'inventory' in self.options, "Missing required keyword argument 'inventory'"
        self.inventory = self.options.get('inventory')
        assert 'host_pattern' in self.options, "Missing required keyword argument 'host_pattern'"
        self.pattern = self.options.get('host_pattern')

        # Initialize ansible inventory manager
        self.initialize_inventory()

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            self.module_name = name
            return self.__run

    def initialize_inventory(self):
        # Initialize inventory_manager with the provided inventory and host_pattern
        try:
            self.inventory_manager = Inventory(self.inventory)
        except ansible.errors.AnsibleError, e:
            # raise
            # pytest.fail(e)
            raise pytest.UsageError(e)
        self.inventory_manager.subset(self.pattern)

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
            module_path=self.options.get('module_path'),
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

        runner = Runner(**kwargs)

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
            raise AnsibleHostUnreachable("Host unreachable", dark=results['dark'], contacted=results['contacted'])

        # No hosts contacted
        # if not results['contacted']:
        #     raise ansible.errors.AnsibleConnectionFailed("Provided hosts list is empty")

        # Success!
        # return results
        return results['contacted']


if has_ansible_v2:
    class ResultAccumulator(CallbackBase):

        def __init__(self, *args, **kwargs):
            super(ResultAccumulator, self).__init__(*args, **kwargs)
            self.contacted = {}
            self.unreachable = {}

        def v2_runner_on_failed(self, result, *args, **kwargs):
            self.contacted[result._host.get_name()] = result._result

        v2_runner_on_ok = v2_runner_on_failed

        def v2_runner_on_unreachable(self, result):
            self.unreachable[result._host.get_name()] = result._result

        @property
        def results(self):
            return dict(contacted=self.contacted, unreachable=self.unreachable)


class AnsibleV2Module(AnsibleV1Module):

    def __init__(self, **kwargs):
        self.loader = None
        self.inventory_manager = None
        self.variable_manager = None

        super(AnsibleV2Module, self).__init__(**kwargs)

    # NOTE: __getattr__ does not follow inheritance correctly, therefore we
    # include it in the subclass
    # https://stackoverflow.com/questions/12047847/super-object-not-calling-getattr
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            self.module_name = name
            return self.__run

    def initialize_inventory(self):
        # Initialize inventory_manager with the provided inventory and host_pattern
        log.debug("initialize_inventory - DataLoader()")
        self.loader = DataLoader()
        log.debug("initialize_inventory - VariableManager()")
        self.variable_manager = VariableManager()

        try:
            log.debug("initialize_inventory - Inventory(host_list=%s)" % self.inventory)
            self.inventory_manager = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list=self.inventory)
        except ansible.errors.AnsibleError, e:
            raise pytest.UsageError(e)
        self.variable_manager.set_inventory(self.inventory_manager)

    def __run(self, *module_args, **complex_args):
        '''
        The API provided by ansible is not intended as a public API.
        '''

        # Assemble module argument string
        if module_args:
            complex_args.update(dict(_raw_params=' '.join(module_args)))

        # Assert hosts matching the provided pattern exist
        hosts = self.inventory_manager.list_hosts(self.pattern)
        if len(hosts) == 0:
            raise AnsibleNoHostsMatch("No hosts match:'%s'" % self.pattern)

        # Log the module and parameters
        log.debug("[%s] %s: %s" % (self.pattern, self.module_name, complex_args))

        parser = CLI.base_parser(
            runas_opts=True,
            async_opts=True,
            output_opts=True,
            connect_opts=True,
            check_opts=True,
            runtask_opts=True,
            vault_opts=True,
            fork_opts=True,
            module_opts=True,
        )
        (options, args) = parser.parse_args([])

        # Pass along cli options
        options.verbosity = 5
        options.connection = self.options.get('connection')
        options.remote_user = self.options.get('user')
        options.become = self.options.get('become')
        options.become_method = self.options.get('become_method')
        options.become_user = self.options.get('become_user')
        options.module_path = self.options.get('module_path')

        # Initialize callback to capture module JSON responses
        cb = ResultAccumulator()

        kwargs = dict(
            inventory=self.inventory_manager,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=options,
            stdout_callback=cb,
            passwords=dict(conn_pass=None, become_pass=None),
        )

        # create a pseudo-play to execute the specified module via a single task
        play_ds = dict(
            name="Ansible Ad-Hoc",
            hosts=self.pattern,
            gather_facts='no',
            tasks=[
                dict(
                    action=dict(
                        module=self.module_name, args=complex_args
                    )
                ),
            ]
        )
        log.debug("__run - Building Play() object - %s" % play_ds)
        play = Play().load(play_ds, variable_manager=self.variable_manager, loader=self.loader)

        # now create a task queue manager to execute the play
        tqm = None
        try:
            log.debug("__run - TaskQueueManager(%s)" % kwargs)
            tqm = TaskQueueManager(**kwargs)
            tqm.run(play)
        finally:
            if tqm:
                tqm.cleanup()

        # Log the results
        log.debug(cb.results)

        # FIXME - should command failures raise an exception, or return?
        # If we choose to raise, callers will need to adapt accordingly
        # Catch any failures in the response
        # for host in results['contacted'].values():
        #     if 'failed' in host or host.get('rc', 0) != 0:
        #         raise Exception("Command failed: %s" % self.module_name, results)

        # Raise exception if host(s) unreachable
        # FIXME - if multiple hosts were involved, should an exception be raised?
        if cb.unreachable:
            # FIXME - unreachable hosts should be included in the exception message
            raise AnsibleHostUnreachable("Host unreachable", dark=cb.unreachable, contacted=cb.contacted)

        # No hosts contacted
        # if not cb.contacted:
        #     raise ansible.errors.AnsibleConnectionFailed("Provided hosts list is empty")

        # Success!
        return cb.contacted
