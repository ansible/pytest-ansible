import logging
import warnings

# conditionally import ansible libraries
import ansible
import ansible.constants
import ansible.utils
import ansible.errors

from pkg_resources import parse_version
has_ansible_v2 = parse_version(ansible.__version__) >= parse_version('2.0.0')

if not has_ansible_v2:
    raise ImportError("Only supported with ansible-2.* and newer")

from ansible.plugins.callback import CallbackBase  # NOQA
from ansible.executor.task_queue_manager import TaskQueueManager  # NOQA
from ansible.playbook.play import Play  # NOQA
from ansible.cli import CLI  # NOQA

from pytest_ansible.module_dispatcher import BaseModuleDispatcher
from pytest_ansible.results import AdHocResult
from pytest_ansible.errors import AnsibleConnectionFailure

try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):

        def emit(self, record):
            pass

log = logging.getLogger(__name__)
log.addHandler(NullHandler())


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


class ModuleDispatcherV2(BaseModuleDispatcher):

    '''Pass.'''
    required_kwargs = ('inventory', 'inventory_manager', 'variable_manager', 'host_pattern', 'loader')

    def has_module(self, name):
        return ansible.plugins.module_loader.has_plugin(name)

    def _run(self, *module_args, **complex_args):
        '''
        The API provided by ansible is not intended as a public API.
        '''

        # Assemble module argument string
        if module_args:
            complex_args.update(dict(_raw_params=' '.join(module_args)))

        # Assert hosts matching the provided pattern exist
        hosts = self.options['inventory_manager'].list_hosts()
        no_hosts = False
        if len(hosts) == 0:
            no_hosts = True
            warnings.warn("provided hosts list is empty, only localhost is available")

        self.options['inventory_manager'].subset(self.options.get('subset'))
        hosts = self.options['inventory_manager'].list_hosts(self.options['host_pattern'])
        if len(hosts) == 0 and not no_hosts:
            raise ansible.errors.AnsibleError("Specified hosts and/or --limit does not match any hosts")

        # Log the module and parameters
        log.debug("[%s] %s: %s" % (self.options['host_pattern'], self.options['module_name'], complex_args))

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
            inventory=self.options['inventory_manager'],
            variable_manager=self.options['variable_manager'],
            loader=self.options['loader'],
            options=options,
            stdout_callback=cb,
            passwords=dict(conn_pass=None, become_pass=None),
        )

        # create a pseudo-play to execute the specified module via a single task
        play_ds = dict(
            name="pytest-ansible",
            hosts=self.options['host_pattern'],
            gather_facts='no',
            tasks=[
                dict(
                    action=dict(
                        module=self.options['module_name'], args=complex_args
                    )
                ),
            ]
        )
        log.debug("_run - Building Play() object - %s", play_ds)
        play = Play().load(play_ds, variable_manager=self.options['variable_manager'], loader=self.options['loader'])

        # now create a task queue manager to execute the play
        tqm = None
        try:
            log.debug("_run - TaskQueueManager(%s)", kwargs)
            tqm = TaskQueueManager(**kwargs)
            tqm.run(play)
        finally:
            if tqm:
                tqm.cleanup()

        # Log the results
        log.debug(cb.results)

        # Raise exception if host(s) unreachable
        # FIXME - if multiple hosts were involved, should an exception be raised?
        if cb.unreachable:
            raise AnsibleConnectionFailure("Host unreachable", dark=cb.unreachable, contacted=cb.contacted)

        # Success!
        return AdHocResult(contacted=cb.contacted)
