import logging
import pytest

import ansible
import ansible.constants
import ansible.utils
import ansible.errors
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

    _dispatch_cls = ModuleDispatcherV1

    def initialize_inventory(self):
        try:
            self.inventory_manager = Inventory(self.inventory)
        except ansible.errors.AnsibleError, e:
            raise pytest.UsageError(e)
        self.inventory_manager.subset(self.pattern)
