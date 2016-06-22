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
    _required_kwargs = ('inventory',)

    def __init__(self, *args, **kwargs):
        self.options = kwargs

        # FIXME - move to has_required_kwargs method
        self.has_required_kwargs(**kwargs)

        # Initialize ansible inventory manager
        if 'inventory_manager' not in self.options or self.options['inventory_manager'] is None:
            self.initialize_inventory()

    def has_required_kwargs(self, **kwargs):
        '''Assert whether the required kwargs were provided during instantiation.
        '''
        for kwarg in self._required_kwargs:
            assert kwarg in self.options, "Missing required keyword argument '%s'" % kwarg

    def __getitem__(self, item):
        # Handle slicing
        if isinstance(item, slice):
            item = "*[(start):(stop)]".format(item)

        if item in self.__dict__:
            return self.__dict__[item]
        else:
            if len(self.options['inventory_manager'].list_hosts(item)) == 0 and item not in self.options['inventory_manager'].groups:
                raise KeyError(item)
            else:
                self.options['host_pattern'] = item
                return self._dispatcher(**self.options)

    def __getattr__(self, attr):
        """Maps values to attributes.
        Only called if there *isn't* an attribute with this name
        """
        if len(self.options['inventory_manager'].list_hosts(attr)) == 0 and attr not in self.options['inventory_manager'].groups:
            raise AttributeError("type HostManager has no attribute '%s'" % attr)
        else:
            self.options['host_pattern'] = attr
            return self._dispatcher(**self.options)

    def keys(self):
        return [h.name for h in self.options['inventory_manager'].list_hosts()]

    def __len__(self):
        return len(self.options['inventory_manager'].list_hosts())

    def __contains__(self, item):
        return len(self.options['inventory_manager'].list_hosts(item)) > 0

    def initialize_inventory(self):
        raise NotImplementedError("Must be implemented by sub-class")


def get_host_manager(*args, **kwargs):
    if has_ansible_v2:
        from .v2 import HostManagerV2 as HostManager
    else:
        from .v1 import HostManagerV1 as HostManager

    return HostManager(*args, **kwargs)
