from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager

from pytest_ansible.host_manager import BaseHostManager
from pytest_ansible.module_dispatcher.v29 import ModuleDispatcherV29


class HostManagerV29(BaseHostManager):
    """Fixme."""

    def __init__(self, *args, **kwargs) -> None:
        """Fixme."""
        super().__init__(*args, **kwargs)
        self._dispatcher = ModuleDispatcherV29

    def initialize_inventory(self):
        self.options["loader"] = DataLoader()
        self.options["inventory_manager"] = InventoryManager(
            loader=self.options["loader"],
            sources=self.options["inventory"],
        )
        self.options["variable_manager"] = VariableManager(
            loader=self.options["loader"],
            inventory=self.options["inventory_manager"],
        )
        if "extra_inventory" in self.options:
            self.options["extra_loader"] = DataLoader()
            self.options["extra_inventory_manager"] = InventoryManager(
                loader=self.options["extra_loader"],
                sources=self.options["extra_inventory"],
            )
            self.options["extra_variable_manager"] = VariableManager(
                loader=self.options["extra_loader"],
                inventory=self.options["extra_inventory_manager"],
            )
