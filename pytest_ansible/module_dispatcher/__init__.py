import ansible.plugins
import ansible.errors


class BaseModuleDispatcher(object):

    '''Pass.'''

    def __init__(self, **kwargs):
        self.options = kwargs

        # Module name is used when accessing an instance attribute (e.g.
        # self.ping)
        self.module_name = None

        required_kwargs = ('inventory', 'inventory_manager', 'variable_manager', 'host_pattern', 'loader')
        for kwarg in required_kwargs:
            assert kwarg in self.options, "Missing required keyword argument '%s'" % kwarg
            setattr(self, kwarg, kwargs.get(kwarg))

    def __len__(self):
        return len(self.inventory_manager.list_hosts(self.host_pattern))

    def __contains__(self, item):
        return len(self.inventory_manager.list_hosts(item)) > 0
        # return self.inventory_manager.get_host(item) is not None

    def __getattr__(self, name):
        if name not in ansible.plugins.module_loader:
            # TODO: should we just raise an AttributeError, or a more
            # raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__.__name__, name))
            raise ansible.errors.AnsibleModuleError("The module {0} was not found in configured module "
                                                    "paths.".format(name))
        else:
            self.module_name = name
            return self._run

    def _run(self, *args, **kwargs):
        '''
        The API provided by ansible is not intended as a public API.
        '''
        raise RuntimeError("Must be implemented by a sub-class")
