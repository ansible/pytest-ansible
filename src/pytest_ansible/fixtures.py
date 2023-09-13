"""PyTest fixtures."""

import pytest


@pytest.fixture()
def ansible_adhoc(request):
    """Return an inventory initialization method."""
    plugin = request.config.pluginmanager.getplugin("ansible")

    def init_host_mgr(**kwargs):
        return plugin.initialize(request.config, request, **kwargs)

    return init_host_mgr


@pytest.fixture()
def ansible_module(ansible_adhoc):
    """Return a subclass of BaseModuleDispatcher."""
    host_mgr = ansible_adhoc()
    return getattr(host_mgr, host_mgr.options["host_pattern"])


@pytest.fixture()
def ansible_facts(ansible_module):
    """Return ansible_facts dictionary."""
    return ansible_module.setup()


@pytest.fixture()
def localhost(request):
    """Return a host manager representing localhost."""
    # NOTE: Do not use ansible_adhoc as a dependent fixture since that will assert specific command-line parameters have
    # been supplied.  In the case of localhost, the parameters are provided as kwargs below.
    plugin = request.config.pluginmanager.getplugin("ansible")
    return plugin.initialize(
        request.config,
        request,
        inventory="localhost,",
        connection="local",
        host_pattern="localhost",
    ).localhost
