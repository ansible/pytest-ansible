import pytest
import warnings
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


@pytest.fixture(scope='class')
def ansible_module_cls(request):
    '''
    Return AnsibleV1Module instance with class scope.
    '''
    warnings.warn("Use of ansible_module_cls is deprecated and will be removed in a future release", DeprecationWarning)
    ansible_helper = request.config.pluginmanager.getplugin("ansible")
    return ansible_helper.initialize(request)


@pytest.fixture(scope='function')
def ansible_module(request):
    '''
    Return AnsibleV1Module instance with function scope.
    '''
    ansible_helper = request.config.pluginmanager.getplugin("ansible")
    return ansible_helper.initialize(request)


@pytest.fixture(scope='function')
def ansible_facts_cls(ansible_module_cls):
    '''
    Return ansible_facts dictionary
    '''
    warnings.warn("Use of ansible_facts_cls is deprecated and will be removed in a future release", DeprecationWarning)
    try:
        return ansible_module_cls.setup()
    except AnsibleHostUnreachable, e:
        log.warning("Hosts unreachable: %s" % e.dark.keys())
        return e.contacted


@pytest.fixture(scope='function')
def ansible_facts(ansible_module):
    '''
    Return ansible_facts dictionary
    '''
    try:
        return ansible_module.setup()
    except AnsibleHostUnreachable, e:
        log.warning("Hosts unreachable: %s" % e.dark.keys())
        return e.contacted
