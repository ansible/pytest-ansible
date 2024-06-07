"""PyTest fixtures."""

import pytest


@pytest.fixture(name="ansible_adhoc")
def fixture_ansible_adhoc(request):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Return an inventory initialization method."""
    plugin = request.config.pluginmanager.getplugin("ansible")

    def init_host_mgr(**kwargs):  # type: ignore[no-untyped-def]  # noqa: ANN003, ANN202
        return plugin.initialize(request.config, request, **kwargs)

    return init_host_mgr


@pytest.fixture(name="ansible_module")
def fixture_ansible_module(ansible_adhoc):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Return a subclass of BaseModuleDispatcher."""
    host_mgr = ansible_adhoc()
    return getattr(host_mgr, host_mgr.options["host_pattern"])


@pytest.fixture()
def ansible_facts(ansible_module):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Return ansible_facts dictionary."""
    return ansible_module.setup()


@pytest.fixture()
def localhost(request):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Return a host manager representing localhost."""
    # NOTE: Do not use ansible_adhoc as a dependent fixture since that will assert specific command-line parameters have  # noqa: E501
    # been supplied.  In the case of localhost, the parameters are provided as kwargs below.
    plugin = request.config.pluginmanager.getplugin("ansible")
    return plugin.initialize(
        request.config,
        request,
        inventory="localhost,",
        connection="local",
        host_pattern="localhost",
    ).localhost
