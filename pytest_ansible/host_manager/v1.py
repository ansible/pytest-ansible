from ansible.inventory import Inventory
from pytest_ansible.logger import get_logger
from pytest_ansible.host_manager import BaseHostManager
from pytest_ansible.module_dispatcher.v1 import ModuleDispatcherV1

log = get_logger(__name__)


class HostManagerV1(BaseHostManager):

    """Fixme."""

    def __init__(self, *args, **kwargs):
        """Fixme."""
        super(HostManagerV1, self).__init__(*args, **kwargs)
        self._dispatcher = ModuleDispatcherV1

    def keys(self):
        return [h for h in self.options['inventory_manager'].list_hosts()]

    def initialize_inventory(self):
        self.options['inventory_manager'] = Inventory(self.options['inventory'])
        # self.options['inventory_manager'].subset(self.pattern)
