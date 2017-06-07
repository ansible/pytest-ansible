from ansible.parsing.dataloader import DataLoader
from pytest_ansible.logger import get_logger
from pytest_ansible.host_manager import BaseHostManager
from pytest_ansible.module_dispatcher.v2 import ModuleDispatcherV2
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager

log = get_logger(__name__)


class HostManagerV24(BaseHostManager):

    """Pass."""

    _dispatcher = ModuleDispatcherV2

    def initialize_inventory(self):
        self.options['loader'] = DataLoader()
        self.options['variable_manager'] = VariableManager(loader=self.options['loader'])
        self.options['inventory_manager'] = InventoryManager(loader=self.options['loader'],
                                                             sources=self.options['inventory'])
        self.options['variable_manager'].set_inventory(self.options['inventory_manager'])
