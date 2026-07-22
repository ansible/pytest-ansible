"""Test the module dispatcher."""

from __future__ import annotations

import sys

from unittest.mock import MagicMock, patch

import ansible.errors
import pytest

from pytest_ansible.module_dispatcher import BaseModuleDispatcher
from pytest_ansible.module_dispatcher.v213 import ModuleDispatcherV213, _execute_play

from .conftest import NEGATIVE_HOST_PATTERNS, POSITIVE_HOST_PATTERNS


def test_type_error() -> None:
    """Verify that BaseModuleDispatcher cannot be instantiated."""
    with pytest.raises(TypeError, match=r"^Can't instantiate.*$"):
        BaseModuleDispatcher(inventory="localhost,")  # type: ignore[abstract] #pylint: disable=abstract-class-instantiated


@pytest.mark.requires_ansible_v2
def test_importerror_requires_v1():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    with pytest.raises(ImportError):
        # pylint: disable=unused-import
        import pytest_ansible.module_dispatcher.v1  # type: ignore[import-not-found] # noqa: F401 # pylint: disable=import-error, no-name-in-module


@pytest.mark.parametrize(
    ("host_pattern", "num_hosts"),
    POSITIVE_HOST_PATTERNS,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_dispatcher_len(host_pattern, num_hosts, hosts, include_extra_inventory):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert len(getattr(hosts, host_pattern)) == num_hosts[include_extra_inventory]


@pytest.mark.parametrize(
    ("host_pattern", "num_hosts"),
    POSITIVE_HOST_PATTERNS,
)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_dispatcher_contains(host_pattern, num_hosts, hosts, include_extra_inventory):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert host_pattern in hosts["all"]


@pytest.mark.parametrize(("host_pattern", "num_hosts"), NEGATIVE_HOST_PATTERNS)
@pytest.mark.parametrize(
    "include_extra_inventory",
    (True, False),
)
def test_dispatcher_not_contains(  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    host_pattern,  # noqa: ANN001
    num_hosts,  # noqa: ANN001, ARG001
    hosts,  # noqa: ANN001
    include_extra_inventory,  # noqa: ANN001
):
    hosts = hosts(include_extra_inventory=include_extra_inventory)
    assert host_pattern not in hosts["all"]


def test_ansible_module_error(hosts):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Verify that AnsibleModuleError is raised when no such module exists."""
    from pytest_ansible.errors import AnsibleModuleError

    all_hosts = hosts().all
    with pytest.raises(AnsibleModuleError) as exc_info:
        all_hosts.a_module_that_most_certainly_does_not_exist()
    assert (
        str(exc_info.value)
        == f"The module {'a_module_that_most_certainly_does_not_exist'} was not found in configured module paths."  # noqa: E501
    )


class _ConcreteDispatcher(BaseModuleDispatcher):
    """Minimal concrete dispatcher for testing base-class branches."""

    def has_module(self, name: str) -> str:  # pylint: disable=useless-parent-delegation
        """Delegate to base implementation for coverage.

        Args:
            name: Module name passed through to the base method

        Returns:
            Result of the base has_module implementation.
        """
        return super().has_module(name)

    def _run(  # pylint: disable=useless-parent-delegation
        self,
        *args: object,
        **kwargs: object,
    ) -> object:
        """Delegate to base implementation for coverage.

        Args:
            *args: Positional args forwarded to the base method
            **kwargs: Keyword args forwarded to the base method

        Returns:
            Result of the base _run implementation.
        """
        return super()._run(*args, **kwargs)  # type: ignore[no-untyped-call]


def test_base_dispatcher_missing_required_kwargs() -> None:
    """BaseModuleDispatcher raises TypeError when required kwargs missing."""
    with pytest.raises(TypeError, match="Missing required keyword argument"):
        _ConcreteDispatcher()


def test_base_dispatcher_abstract_method_bodies() -> None:
    """Cover abstract method bodies via super() calls from a concrete subclass."""
    dispatcher = _ConcreteDispatcher(inventory="localhost,")
    assert not dispatcher.has_module("ping")
    with pytest.raises(RuntimeError, match="Must be implemented by a sub-class"):
        dispatcher._run()


def test_v213_reload_without_custom_loader_support() -> None:
    """Cover ImportError path that disables HAS_CUSTOM_LOADER_SUPPORT."""
    import builtins
    import importlib

    import ansible.plugins.loader as real_loader

    import pytest_ansible.module_dispatcher.v213 as v213_mod

    original = getattr(real_loader, "init_plugin_loader", None)
    real_import = builtins.__import__

    def fake_import(
        name: str,
        globals: object = None,  # noqa: A002
        locals: object = None,  # noqa: A002
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        if fromlist and "init_plugin_loader" in fromlist:
            msg = "init_plugin_loader unavailable"
            raise ImportError(msg)
        return real_import(name, globals, locals, fromlist, level)  # type: ignore[arg-type]

    try:
        if original is not None:
            del real_loader.init_plugin_loader
        with patch("builtins.__import__", side_effect=fake_import):
            reloaded = importlib.reload(v213_mod)
        assert reloaded.HAS_CUSTOM_LOADER_SUPPORT is False
    finally:
        if original is not None:
            real_loader.init_plugin_loader = original
        importlib.reload(v213_mod)

    assert v213_mod.HAS_CUSTOM_LOADER_SUPPORT is True


def test_execute_play_tqm_init_failure() -> None:
    """_execute_play cleanup is skipped when TaskQueueManager construction fails."""
    with (
        patch(
            "pytest_ansible.module_dispatcher.v213.TaskQueueManager",
            side_effect=RuntimeError("tqm init failed"),
        ),
        pytest.raises(RuntimeError, match="tqm init failed"),
    ):
        _execute_play(MagicMock(), {}, MagicMock())


def test_module_dispatcher_v213_requires_ansible() -> None:
    """ModuleDispatcherV213 raises ImportError when ansible < 2.13."""
    with (
        patch("pytest_ansible.module_dispatcher.v213.has_ansible_v213", new=False),
        pytest.raises(ImportError, match=r"Only supported with ansible-2\.13"),
    ):
        ModuleDispatcherV213(
            inventory="localhost,",
            inventory_manager=MagicMock(),
            variable_manager=MagicMock(),
            host_pattern="all",
            loader=MagicMock(),
        )


def test_module_dispatcher_has_module_string_path() -> None:
    """has_module accepts a single string module_path."""
    dispatcher = ModuleDispatcherV213.__new__(ModuleDispatcherV213)
    dispatcher.options = {
        "inventory": "localhost,",
        "inventory_manager": MagicMock(),
        "variable_manager": MagicMock(),
        "host_pattern": "all",
        "loader": MagicMock(),
        "module_path": "/tmp/modules",  # noqa: S108
    }
    with patch("pytest_ansible.module_dispatcher.v213.module_loader") as mock_loader:
        found = MagicMock()
        found.resolved = True
        found.resolved_fqcn = "ansible.builtin.ping"
        mock_loader.find_plugin_with_context.return_value = found
        assert dispatcher.has_module("ping") == "ansible.builtin.ping"
        mock_loader.add_directory.assert_called_with("/tmp/modules")  # noqa: S108


def test_module_dispatcher_has_module_not_found() -> None:
    """has_module returns empty string on ModuleNotFoundError."""
    dispatcher = ModuleDispatcherV213.__new__(ModuleDispatcherV213)
    dispatcher.options = {
        "inventory": "localhost,",
        "inventory_manager": MagicMock(),
        "variable_manager": MagicMock(),
        "host_pattern": "all",
        "loader": MagicMock(),
    }
    with patch("pytest_ansible.module_dispatcher.v213.module_loader") as mock_loader:
        mock_loader.find_plugin_with_context.side_effect = ModuleNotFoundError("missing")
        assert not dispatcher.has_module("nope")


def test_module_dispatcher_run_without_custom_loader() -> None:
    """_run skips init_plugin_loader when custom loader support is absent."""
    dispatcher = ModuleDispatcherV213.__new__(ModuleDispatcherV213)
    dispatcher.options = {
        "inventory": "localhost,",
        "inventory_manager": MagicMock(),
        "variable_manager": MagicMock(),
        "host_pattern": "localhost",
        "loader": MagicMock(),
        "module_name": "ping",
    }
    dispatcher.options["inventory_manager"].list_hosts.return_value = [MagicMock()]

    with (
        patch.object(dispatcher, "_assert_hosts_exist"),
        patch.object(dispatcher, "_configure_adhoc_cli"),
        patch.object(dispatcher, "_build_tqm_kwargs", return_value={}),
        patch.object(dispatcher, "_build_play_ds", return_value={}),
        patch("pytest_ansible.module_dispatcher.v213.Play") as mock_play,
        patch("pytest_ansible.module_dispatcher.v213._execute_play"),
        patch("pytest_ansible.module_dispatcher.v213.HAS_CUSTOM_LOADER_SUPPORT", new=False),
        patch("pytest_ansible.module_dispatcher.v213.init_plugin_loader") as mock_init,
        patch.object(dispatcher, "_raise_on_unreachable"),
    ):
        mock_play.return_value.load.return_value = MagicMock()
        dispatcher._run()  # type: ignore[no-untyped-call]

    mock_init.assert_not_called()


def test_module_dispatcher_run_with_module_args() -> None:
    """_run merges positional module args into complex_args."""
    dispatcher = ModuleDispatcherV213.__new__(ModuleDispatcherV213)
    dispatcher.options = {
        "inventory": "localhost,",
        "inventory_manager": MagicMock(),
        "variable_manager": MagicMock(),
        "host_pattern": "localhost",
        "loader": MagicMock(),
        "module_name": "ping",
    }
    dispatcher.options["inventory_manager"].list_hosts.return_value = [MagicMock()]

    with (
        patch.object(dispatcher, "_assert_hosts_exist"),
        patch.object(dispatcher, "_configure_adhoc_cli"),
        patch.object(dispatcher, "_build_tqm_kwargs", return_value={}),
        patch.object(
            dispatcher,
            "_build_play_ds",
            side_effect=lambda complex_args: {"args": complex_args},
        ) as mock_ds,
        patch("pytest_ansible.module_dispatcher.v213.Play") as mock_play,
        patch("pytest_ansible.module_dispatcher.v213._execute_play"),
        patch("pytest_ansible.module_dispatcher.v213.HAS_CUSTOM_LOADER_SUPPORT", new=True),
        patch("pytest_ansible.module_dispatcher.v213.init_plugin_loader"),
        patch.object(dispatcher, "_raise_on_unreachable"),
    ):
        mock_play.return_value.load.return_value = MagicMock()
        result = dispatcher._run("arg1", "arg2")  # type: ignore[no-untyped-call]

    assert "arg1" in mock_ds.call_args[0][0]["_raw_params"]
    assert result.contacted == {}


def test_module_dispatcher_assert_hosts_exist_no_match() -> None:
    """_assert_hosts_exist raises when subset matches no hosts."""
    dispatcher = ModuleDispatcherV213.__new__(ModuleDispatcherV213)
    inv = MagicMock()
    host = MagicMock()
    inv.list_hosts.side_effect = [[host], []]
    dispatcher.options = {
        "inventory_manager": inv,
        "host_pattern": "nomatch",
        "subset": "nomatch",
    }
    with pytest.raises(ansible.errors.AnsibleError, match="does not match any hosts"):
        dispatcher._assert_hosts_exist()


def test_module_dispatcher_configure_adhoc_cli_verbosity_and_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_configure_adhoc_cli handles verbosity and boolean option flags.

    Args:
        monkeypatch: pytest monkeypatch fixture
    """
    dispatcher = ModuleDispatcherV213.__new__(ModuleDispatcherV213)
    dispatcher.options = {
        "host_pattern": "localhost",
        "connection": "local",
        "become": True,
        "user": None,
    }
    monkeypatch.setattr(sys, "argv", ["pytest", "-vv", "tests"])

    with patch("pytest_ansible.module_dispatcher.v213.AdHocCLI") as mock_cli:
        mock_cli.return_value.parse = MagicMock()
        dispatcher._configure_adhoc_cli()
        args = mock_cli.call_args[0][0]
        assert "-vv" in args
        assert "--become" in args
        assert "--connection=local" in args
