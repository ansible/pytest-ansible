import pytest
from pytest_ansible.logger import get_logger

__all__ = ['ansible_module', 'ansible_facts', 'ansible_adhoc']
log = get_logger(__name__)


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


@pytest.fixture(scope='function')
def localhost(request):
    '''
    Return a host manager representing localhost
    '''
    # NOTE: Do not use ansible_adhoc as a dependent fixture since that will assert specific command-line parameters have
    # been supplied.  In the case of localhost, the parameters are provided as kwargs below.
    plugin = request.config.pluginmanager.getplugin("ansible")
    return plugin.initialize(request, inventory='localhost,', connection='local', host_pattern='localhost').localhost
