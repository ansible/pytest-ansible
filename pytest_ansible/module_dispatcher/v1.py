import warnings
import ansible
import ansible.constants
import ansible.utils
import ansible.errors

from ansible.runner import Runner
from pytest_ansible.module_dispatcher import BaseModuleDispatcher
from pytest_ansible.errors import AnsibleConnectionFailure
from pytest_ansible.results import AdHocResult
from pytest_ansible.has_version import has_ansible_v1


if not has_ansible_v1:
    raise ImportError("Only supported with ansible < 2.0")


class ModuleDispatcherV1(BaseModuleDispatcher):

    """Pass."""

    required_kwargs = ('inventory', 'inventory_manager', 'host_pattern')

    def has_module(self, name):
        # Make sure we parse module_path and pass it to the loader,
        # otherwise, only built-in modules will work.
        if 'module_path' in self.options:
            paths = self.options['module_path']
            if isinstance(paths, (list, tuple, set)):
                for path in paths:
                    ansible.utils.module_finder.add_directory(path)
            else:
                ansible.utils.module_finder.add_directory(paths)

        return ansible.utils.module_finder.has_plugin(name)

    def _run(self, *module_args, **complex_args):
        """Execute an ansible adhoc command returning the results in a AdHocResult object."""
        # Assemble module argument string
        if True:
            module_args = ' '.join(module_args)
        else:
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

        # Build module runner object
        kwargs = dict(
            inventory=self.options.get('inventory_manager'),
            pattern=self.options.get('host_pattern'),
            module_name=self.options.get('module_name'),
            module_args=module_args,
            complex_args=complex_args,
            transport=self.options.get('connection'),
            remote_user=self.options.get('user'),
            module_path=self.options.get('module_path'),
            become=self.options.get('become'),
            become_method=self.options.get('become_method'),
            become_user=self.options.get('become_user'),
        )

        # Run the module
        runner = Runner(**kwargs)
        results = runner.run()


        if 'dark' in results and results['dark']:
            raise AnsibleConnectionFailure("Host unreachable", dark=results['dark'], contacted=results['contacted'])

        # Success!
        return AdHocResult(contacted=results['contacted'])
