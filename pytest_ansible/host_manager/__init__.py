import logging
import ansible
from pkg_resources import parse_version

# conditionally import ansible libraries
has_ansible_v2 = parse_version(ansible.__version__) >= parse_version('2.0.0')

try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):

        def emit(self, record):
            pass

log = logging.getLogger(__name__)
log.addHandler(NullHandler())


class BaseHostManager(object):

    '''Pass.'''
    _dispatcher = Exception

    def __init__(self, *args, **kwargs):
        self.options = kwargs

        assert 'inventory' in self.options, "Missing required keyword argument 'inventory'"
        self.inventory = self.options.get('inventory')

        # Initialize ansible inventory manager
        if not hasattr(self, 'inventory_manager') or self.inventory_manager is None:
            self.initialize_inventory()

    def __getitem__(self, item):
        # Handle slicing
        if isinstance(item, slice):
            item = "*[(start):(stop)]".format(item)

        if item in self.__dict__:
            return self.__dict__[item]
        else:
            if len(self.inventory_manager.list_hosts(item)) == 0 and item not in self.inventory_manager.groups:
                raise KeyError(item)
            else:
                self.options['host_pattern'] = item
                return self._dispatcher(inventory_manager=self.inventory_manager,
                                        variable_manager=self.variable_manager, loader=self.loader,
                                        **self.options)

    def __getattr__(self, attr):
        """Maps values to attributes.
        Only called if there *isn't* an attribute with this name
        """
        if len(self.inventory_manager.list_hosts(attr)) == 0 and attr not in self.inventory_manager.groups:
            raise AttributeError("type HostManager has no attribute '%s'" % attr)
        else:
            print self.options
            self.options['host_pattern'] = attr
            return self._dispatcher(inventory_manager=self.inventory_manager, variable_manager=self.variable_manager,
                                    loader=self.loader, **self.options)

    def keys(self):
        return [h.name for h in self.inventory_manager.list_hosts()]

    def __len__(self):
        return len(self.inventory_manager.list_hosts())

    def __contains__(self, item):
        return len(self.inventory_manager.list_hosts(item)) > 0

    def initialize_inventory(self):
        raise NotImplementedError("Must be implemented by sub-class")


def get_host_manager(*args, **kwargs):
    if has_ansible_v2:
        from .v2 import HostManagerV2 as HostManager
    else:
        from .v1 import HostManagerV1 as HostManager

    return HostManager(*args, **kwargs)
