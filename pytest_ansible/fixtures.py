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

__all__ = ['ansible_module', 'ansible_facts', 'host_manager']

log = logging.getLogger(__name__)
log.addHandler(NullHandler())


# FIXME - consider ansible_adhoc name instead
@pytest.fixture(scope='function')
def host_manager(request):
    plugin = request.config.pluginmanager.getplugin("ansible")

    def init_host_mgr(**kwargs):
        return plugin.initialize(request, **kwargs)
    return init_host_mgr


@pytest.fixture(scope='function')
def ansible_module(host_manager):
    '''
    Return AnsibleV1Module instance with function scope.
    '''
    return host_manager().all


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
