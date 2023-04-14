from ansible.inventory import Inventory

from pytest_ansible.host_manager import BaseHostManager
from pytest_ansible.module_dispatcher.v1 import ModuleDispatcherV1


class HostManagerV1(BaseHostManager):
    """Fixme."""

    def __init__(self, *args, **kwargs) -> None:
        """Fixme."""
        super().__init__(*args, **kwargs)
        self._dispatcher = ModuleDispatcherV1

    def keys(self):
        return list(self.options["inventory_manager"].list_hosts())

    def initialize_inventory(self):
        self.options["inventory_manager"] = Inventory(self.options["inventory"])
