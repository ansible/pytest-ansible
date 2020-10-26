from ansible.parsing.dataloader import DataLoader
from pytest_ansible.host_manager import BaseHostManager
from pytest_ansible.module_dispatcher.v2 import ModuleDispatcherV2
from ansible.vars import VariableManager
from ansible.inventory import Inventory


class HostManagerV2(BaseHostManager):

    """Fixme."""

    def __init__(self, *args, **kwargs):
        """Fixme."""
        super(HostManagerV2, self).__init__(*args, **kwargs)
        self._dispatcher = ModuleDispatcherV2

    def initialize_inventory(self):

        self.options['loader'] = DataLoader()
        self.options['variable_manager'] = VariableManager()
        self.options['inventory_manager'] = Inventory(loader=self.options['loader'],
                                                      variable_manager=self.options['variable_manager'],
                                                      host_list=self.options['inventory'])
        self.options['variable_manager'].set_inventory(self.options['inventory_manager'])
