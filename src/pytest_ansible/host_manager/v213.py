"""Fixme."""

from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager

from pytest_ansible.host_manager.base import BaseHostManager
from pytest_ansible.module_dispatcher.v213 import ModuleDispatcherV213


class HostManagerV213(BaseHostManager):
    """Fixme."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN002, ANN003
        """Fixme."""
        super().__init__(*args, **kwargs)
        self._dispatcher = ModuleDispatcherV213

    def initialize_inventory(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Fixme."""
        self.options["loader"] = DataLoader()
        self.options["inventory_manager"] = InventoryManager(
            loader=self.options["loader"],
            sources=self.options["inventory"],
        )
        self.options["variable_manager"] = VariableManager(
            loader=self.options["loader"],
            inventory=self.options["inventory_manager"],
        )
        if self.options.get("extra_inventory", None):
            self.options["extra_loader"] = DataLoader()
            self.options["extra_inventory_manager"] = InventoryManager(
                loader=self.options["extra_loader"],
                sources=self.options["extra_inventory"],
            )
            self.options["extra_variable_manager"] = VariableManager(
                loader=self.options["extra_loader"],
                inventory=self.options["extra_inventory_manager"],
            )
