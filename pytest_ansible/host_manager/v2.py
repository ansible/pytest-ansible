import logging

import ansible
import ansible.constants
import ansible.utils
import ansible.errors
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
        self.loader = DataLoader()
        self.variable_manager = VariableManager()

        try:
            self.inventory_manager = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list=self.inventory)
        except ansible.errors.AnsibleError, e:
            raise Exception(e)
        self.variable_manager.set_inventory(self.inventory_manager)
