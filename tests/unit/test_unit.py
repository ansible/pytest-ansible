"""Basic unit tests."""

from __future__ import annotations

import logging
import re
import subprocess  # noqa: S404
import sys

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from pytest_ansible.module_dispatcher.v213 import (
    ModuleDispatcherV213,
    ResultAccumulator,
    _execute_play,
)
from pytest_ansible.molecule import _populate_config_metadata
from pytest_ansible.units import _resolve_collections_dir, inject, inject_only


if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_inject(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test injecting a path.

    :param monkeypatch: The pytest monkeypatch fixture
    :param tmp_path: The pytest tmp_path fixture
    :param caplog: The pytest caplog fixture
    """
    caplog.set_level(logging.DEBUG)

    def mock_get_collection_name(start_path: Path) -> tuple[str | None, str | None]:  # noqa: ARG001
        """Mock the get_collection_name function.

        Args:
            start_path: The Path to the root of the collection

        Returns:
            A tuple of the namespace and name
        """
        return "namespace", "name"

    monkeypatch.setattr(
        "pytest_ansible.units.get_collection_name",
        mock_get_collection_name,
    )

    (tmp_path / "collections" / "ansible_collections").mkdir(parents=True)

    inject(tmp_path)
    assert (tmp_path / "collections" / "ansible_collections" / "namespace" / "name").is_dir()
    assert (
        str(tmp_path / "collections")
        == sys.path[0]
        == re.search(r"_ACF installed: \['(.*?)'.*]", caplog.text).groups()[0]  # type: ignore[union-attr]
        == re.search(r"_ACF configured paths: \['(.*?)'.*]", caplog.text).groups()[0]  # type: ignore[union-attr]
    )


def test_inject_only(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test only injecting a path.

    :param monkeypatch: The pytest monkeypatch fixture
    :param tmp_path: The pytest tmp_path fixture
    :param caplog: The pytest caplog fixture
    """
    caplog.set_level(logging.DEBUG)
    monkeypatch.setenv("ANSIBLE_COLLECTIONS_PATH", str(tmp_path / "collections"))

    (tmp_path / "collections" / "ansible_collections").mkdir(parents=True)

    inject_only()
    assert (
        str(tmp_path / "collections")
        == sys.path[0]
        == re.search(r"_ACF installed: \['(.*?)'.*]", caplog.text).groups()[0]  # type: ignore[union-attr]
        == re.search(r"_ACF configured paths: \['(.*?)'.*]", caplog.text).groups()[0]  # type: ignore[union-attr]
    )


def test_resolve_collections_dir_in_tree(tmp_path: Path) -> None:
    """Test _resolve_collections_dir when already inside a collection tree.

    :param tmp_path: The pytest tmp_path fixture
    """
    tree = tmp_path / "collections" / "ansible_collections" / "namespace" / "name"
    tree.mkdir(parents=True)
    result = _resolve_collections_dir(tree, "namespace", "name")
    assert result == tmp_path / "collections"


def test_populate_config_metadata_no_metadata() -> None:
    """Test _populate_config_metadata returns early when config lacks _metadata."""

    class FakeConfig:
        """Config object without _metadata attribute."""

    _populate_config_metadata(FakeConfig())


def test_populate_config_metadata_with_metadata() -> None:
    """Test _populate_config_metadata populates metadata correctly."""

    class FakeConfig:
        """Config object with a _metadata dict."""

        def __init__(self) -> None:
            self._metadata: dict = {"Packages": {}}  # type: ignore[type-arg]

    config = FakeConfig()
    _populate_config_metadata(config)
    assert "molecule" in config._metadata["Packages"]
    assert "Tools" in config._metadata
    assert "ansible" in config._metadata["Tools"]
    assert "env" in config._metadata


def test_populate_config_metadata_captures_env_vars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test _populate_config_metadata captures matching environment variables.

    Args:
        monkeypatch: pytest monkeypatch fixture
    """

    class FakeConfig:
        """Config object with a _metadata dict."""

        def __init__(self) -> None:
            self._metadata: dict = {"Packages": {}}  # type: ignore[type-arg]

    monkeypatch.setenv("ANSIBLE_TEST_VAR", "yes")
    monkeypatch.setenv("MOLECULE_DEBUG", "1")

    config = FakeConfig()
    _populate_config_metadata(config)
    assert "ANSIBLE_TEST_VAR=yes" in config._metadata["env"]
    assert "MOLECULE_DEBUG=1" in config._metadata["env"]


def test_populate_config_metadata_tools_already_exists() -> None:
    """Test _populate_config_metadata when Tools key already exists in metadata."""

    class FakeConfig:
        """Config object with _metadata including pre-existing Tools."""

        def __init__(self) -> None:
            self._metadata: dict = {  # type: ignore[type-arg]
                "Packages": {},
                "Tools": {"existing_tool": "1.0"},
            }

    config = FakeConfig()
    _populate_config_metadata(config)
    assert "existing_tool" in config._metadata["Tools"]
    assert "ansible" in config._metadata["Tools"]


def test_resolve_collections_dir_existing_dir(tmp_path: Path) -> None:
    """Test _resolve_collections_dir when name_dir already exists.

    :param tmp_path: The pytest tmp_path fixture
    """
    collections_dir = tmp_path / "collections"
    name_dir = collections_dir / "ansible_collections" / "ns" / "col"
    name_dir.mkdir(parents=True)

    result = _resolve_collections_dir(tmp_path, "ns", "col")
    assert result == collections_dir


def test_resolve_collections_dir_creates_symlinks(tmp_path: Path) -> None:
    """Test _resolve_collections_dir creates symlinks when name_dir does not exist.

    :param tmp_path: The pytest tmp_path fixture
    """
    (tmp_path / "module_a.py").write_text("# module a")
    (tmp_path / "README.md").write_text("# readme")

    result = _resolve_collections_dir(tmp_path, "ns", "col")
    name_dir = tmp_path / "collections" / "ansible_collections" / "ns" / "col"
    assert result == tmp_path / "collections"
    assert name_dir.is_dir()
    assert (name_dir / "module_a.py").is_symlink()
    assert (name_dir / "README.md").is_symlink()
    assert not (name_dir / "collections").exists()


def test_for_params():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Test for params."""
    proc = subprocess.run(
        "pytest --help",  # noqa: S607
        shell=True,
        capture_output=True,
        check=False,
    )
    assert "--ansible-unit-inject-only" in proc.stdout.decode()


def test_raise_on_unreachable_extra_callback() -> None:
    """Test _raise_on_unreachable raises for unreachable hosts in extra callback."""
    import pytest

    from pytest_ansible.errors import AnsibleConnectionFailure

    callback = ResultAccumulator()
    callback_extra = ResultAccumulator()
    callback_extra.unreachable = {"extra_host": {"msg": "unreachable"}}
    callback_extra.contacted = {}

    with pytest.raises(AnsibleConnectionFailure, match="extra inventory"):
        ModuleDispatcherV213._raise_on_unreachable(callback, callback_extra)


def test_raise_on_unreachable_primary_callback() -> None:
    """Test _raise_on_unreachable raises for unreachable hosts in primary callback."""
    import pytest

    from pytest_ansible.errors import AnsibleConnectionFailure

    callback = ResultAccumulator()
    callback.unreachable = {"host1": {"msg": "unreachable"}}
    callback.contacted = {}

    with pytest.raises(AnsibleConnectionFailure, match="Host unreachable"):
        ModuleDispatcherV213._raise_on_unreachable(callback, None)


def test_raise_on_unreachable_no_unreachable() -> None:
    """Test _raise_on_unreachable does not raise when all hosts reachable."""
    callback = ResultAccumulator()
    callback_extra = ResultAccumulator()

    ModuleDispatcherV213._raise_on_unreachable(callback, callback_extra)


def test_result_accumulator_on_failed() -> None:
    """Test ResultAccumulator.v2_runner_on_failed records failures."""
    acc = ResultAccumulator()
    result = MagicMock()
    result._host.get_name.return_value = "host1"
    result._result = {"rc": 1, "stderr": "error"}

    acc.v2_runner_on_failed(result)  # type: ignore[no-untyped-call]
    assert "host1" in acc.contacted
    assert acc.contacted["host1"]["failed"] is True
    assert acc.contacted["host1"]["rc"] == 1


def test_result_accumulator_results_property() -> None:
    """Test ResultAccumulator.results property returns expected dict."""
    acc = ResultAccumulator()
    result = MagicMock()
    result._host.get_name.return_value = "h1"
    result._result = {"changed": True}
    acc.v2_runner_on_ok(result)  # type: ignore[no-untyped-call]

    assert acc.results == {"contacted": {"h1": {"changed": True}}, "unreachable": {}}


def test_execute_play_non_v219() -> None:
    """Test _execute_play when has_ansible_v219 is False."""
    mock_tqm_instance = MagicMock()

    with (
        patch(
            "pytest_ansible.module_dispatcher.v213.TaskQueueManager",
            return_value=mock_tqm_instance,
        ),
        patch("pytest_ansible.module_dispatcher.v213.has_ansible_v219", False),  # noqa: FBT003
    ):
        play = MagicMock()
        callback = ResultAccumulator()
        _execute_play(play, {}, callback)

    mock_tqm_instance.run.assert_called_once_with(play)
    mock_tqm_instance.cleanup.assert_called_once()
    mock_tqm_instance.load_callbacks.assert_not_called()


def test_execute_play_v219_empty_callback_plugins() -> None:
    """Test _execute_play with v219 when _callback_plugins is empty."""
    mock_tqm_instance = MagicMock()
    mock_tqm_instance._callback_plugins = []

    with (
        patch(
            "pytest_ansible.module_dispatcher.v213.TaskQueueManager",
            return_value=mock_tqm_instance,
        ),
        patch("pytest_ansible.module_dispatcher.v213.has_ansible_v219", True),  # noqa: FBT003
    ):
        play = MagicMock()
        callback = MagicMock(spec=ResultAccumulator)
        _execute_play(play, {}, callback)

    mock_tqm_instance.load_callbacks.assert_called_once()
    mock_tqm_instance.run.assert_called_once_with(play)


def test_execute_play_v219_with_callback_plugins() -> None:
    """Test _execute_play with v219 replaces the first callback plugin."""
    mock_tqm_instance = MagicMock()
    original_plugin = MagicMock()
    mock_tqm_instance._callback_plugins = [original_plugin]

    with (
        patch(
            "pytest_ansible.module_dispatcher.v213.TaskQueueManager",
            return_value=mock_tqm_instance,
        ),
        patch("pytest_ansible.module_dispatcher.v213.has_ansible_v219", True),  # noqa: FBT003
    ):
        play = MagicMock()
        callback = MagicMock(spec=ResultAccumulator)
        _execute_play(play, {}, callback)

    assert mock_tqm_instance._callback_plugins[0] is callback


def test_result_accumulator_on_unreachable() -> None:
    """Test ResultAccumulator.v2_runner_on_unreachable records unreachable hosts."""
    acc = ResultAccumulator()
    result = MagicMock()
    result._host.get_name.return_value = "unreachable_host"
    result._result = {"msg": "No route to host"}

    acc.v2_runner_on_unreachable(result)  # type: ignore[no-untyped-call]
    assert "unreachable_host" in acc.unreachable
    assert acc.unreachable["unreachable_host"]["msg"] == "No route to host"


def test_build_tqm_kwargs_non_v219() -> None:
    """Test _build_tqm_kwargs includes stdout_callback when not v219."""
    dispatcher = MagicMock(spec=ModuleDispatcherV213)
    dispatcher.options = {
        "inventory_manager": MagicMock(),
        "variable_manager": MagicMock(),
        "loader": MagicMock(),
    }
    callback = ResultAccumulator()

    with patch("pytest_ansible.module_dispatcher.v213.has_ansible_v219", False):  # noqa: FBT003
        result = ModuleDispatcherV213._build_tqm_kwargs(dispatcher, callback)

    assert result["stdout_callback"] is callback
    assert "stdout_callback_name" not in result


def test_build_tqm_kwargs_extra() -> None:
    """Test _build_tqm_kwargs with extra=True uses extra_ prefixed options."""
    dispatcher = MagicMock(spec=ModuleDispatcherV213)
    extra_inv = MagicMock()
    extra_vm = MagicMock()
    extra_loader = MagicMock()
    dispatcher.options = {
        "inventory_manager": MagicMock(),
        "variable_manager": MagicMock(),
        "loader": MagicMock(),
        "extra_inventory_manager": extra_inv,
        "extra_variable_manager": extra_vm,
        "extra_loader": extra_loader,
    }
    callback = ResultAccumulator()

    with patch("pytest_ansible.module_dispatcher.v213.has_ansible_v219", True):  # noqa: FBT003
        result = ModuleDispatcherV213._build_tqm_kwargs(dispatcher, callback, extra=True)

    assert result["inventory"] is extra_inv
    assert result["variable_manager"] is extra_vm
    assert result["loader"] is extra_loader
