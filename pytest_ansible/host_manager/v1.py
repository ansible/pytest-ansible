import logging
from ansible.inventory import Inventory
from pytest_ansible.host_manager import BaseHostManager
from pytest_ansible.module_dispatcher.v1 import ModuleDispatcherV1

try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):

        def emit(self, record):
            pass

log = logging.getLogger(__name__)
log.addHandler(NullHandler())


class HostManagerV1(BaseHostManager):

    '''FIXME'''

    _dispatcher = ModuleDispatcherV1

    def keys(self):
        return [h for h in self.options['inventory_manager'].list_hosts()]

    def initialize_inventory(self):
        self.options['inventory_manager'] = Inventory(self.options['inventory'])
        # self.options['inventory_manager'].subset(self.pattern)
