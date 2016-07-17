import pytest
import logging

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
def ansible_module(request, ansible_adhoc):
    '''
    Return AnsibleV1Module instance with function scope.
    '''
    # `all` returns all hosts in the inventory, regardless of the provided `host_pattern`
    # return ansible_adhoc().all
    host_mgr = ansible_adhoc()
    return getattr(host_mgr, host_mgr.options['host_pattern'])


@pytest.fixture(scope='function')
def ansible_facts(ansible_module):
    '''
    Return ansible_facts dictionary
    '''
    return ansible_module.setup()
