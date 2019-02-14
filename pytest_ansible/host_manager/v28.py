from ansible.parsing.dataloader import DataLoader
from pytest_ansible.logger import get_logger
from pytest_ansible.host_manager import BaseHostManager
from pytest_ansible.module_dispatcher.v28 import ModuleDispatcherV28
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager

log = get_logger(__name__)


class HostManagerV28(BaseHostManager):

    """Fixme."""

    def __init__(self, *args, **kwargs):
        """Fixme."""
        super(HostManagerV28, self).__init__(*args, **kwargs)
        self._dispatcher = ModuleDispatcherV28

    def initialize_inventory(self):
        log.debug("HostManagerV28.initialize_inventory()")
        self.options['loader'] = DataLoader()
        self.options['inventory_manager'] = InventoryManager(loader=self.options['loader'],
                                                             sources=self.options['inventory'])
        self.options['variable_manager'] = VariableManager(loader=self.options['loader'],
                                                           inventory=self.options['inventory_manager'])
        # self.options['inventory_manager'].clear_caches()
