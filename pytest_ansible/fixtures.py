import pytest
import logging
from .errors import AnsibleHostUnreachable

try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):

        def emit(self, record):
            pass

log = logging.getLogger(__name__)
log.addHandler(NullHandler())


@pytest.fixture(scope='function')
def ansible_module(request):
    '''
    Return AnsibleV1Module instance with function scope.
    '''
    ansible_helper = request.config.pluginmanager.getplugin("ansible")
    hosts_mgr = ansible_helper.initialize(request)
    return hosts_mgr.all


@pytest.fixture(scope='function')
def ansible_facts(ansible_module):
    '''
    Return ansible_facts dictionary
    '''
    try:
        return ansible_module.all.setup()
    except AnsibleHostUnreachable, e:
        log.warning("Hosts unreachable: %s" % e.dark.keys())
        return e.contacted
