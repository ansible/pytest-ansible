"""Basic unit tests."""

from __future__ import annotations

import logging
import re
import subprocess  # noqa: S404
import sys

from typing import TYPE_CHECKING

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
    """Test _populate_config_metadata captures matching environment variables."""

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


def test_for_params():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Test for params."""
    proc = subprocess.run(
        "pytest --help",  # noqa: S607
        shell=True,
        capture_output=True,
        check=False,
    )
    assert "--ansible-unit-inject-only" in proc.stdout.decode()
