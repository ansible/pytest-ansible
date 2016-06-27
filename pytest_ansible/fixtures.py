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

__all__ = ['ansible_module', 'ansible_facts', 'ansible_adhoc']

log = logging.getLogger(__name__)
log.addHandler(NullHandler())


@pytest.fixture(scope='function')
def ansible_adhoc(request):
    plugin = request.config.pluginmanager.getplugin("ansible")

    def init_host_mgr(**kwargs):
        return plugin.initialize(request, **kwargs)
    return init_host_mgr


@pytest.fixture(scope='function')
def ansible_module(ansible_adhoc):
    '''
    Return AnsibleV1Module instance with function scope.
    '''
    return ansible_adhoc().all


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
