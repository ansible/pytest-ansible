import logging
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from pytest_ansible.host_manager import BaseHostManager
from pytest_ansible.module_dispatcher.v2 import ModuleDispatcherV2

try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):

        def emit(self, record):
            pass

log = logging.getLogger(__name__)
log.addHandler(NullHandler())


class HostManagerV2(BaseHostManager):

    '''Pass.'''
    _dispatcher = ModuleDispatcherV2

    def initialize_inventory(self):
        self.options['loader'] = DataLoader()
        self.options['variable_manager'] = VariableManager()
        self.options['inventory_manager'] = Inventory(loader=self.options['loader'], variable_manager=self.options['variable_manager'], host_list=self.options['inventory'])
        self.options['variable_manager'].set_inventory(self.options['inventory_manager'])
