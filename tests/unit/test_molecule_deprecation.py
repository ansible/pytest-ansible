"""Unit tests for molecule-via-pytest deprecation and molecule.py coverage."""

from __future__ import annotations

import io
import logging
import sys
import warnings

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from pytest_ansible import molecule as molecule_mod
from pytest_ansible.molecule import (
    MOLECULE_DEPRECATION,
    MoleculeExceptionError,
    MoleculeFile,
    MoleculeItem,
    MoleculeScenario,
    molecule_pytest_configure,
    warn_molecule_deprecated,
)
from pytest_ansible.plugin import pytest_load_initial_conftests


@pytest.fixture(autouse=True)
def _reset_molecule_deprecation_flag() -> None:
    """Ensure each test can observe a fresh deprecation warning."""
    molecule_mod._molecule_deprecation_warned = False


def test_warn_molecule_deprecated_emits_once() -> None:
    """warn_molecule_deprecated should emit a single DeprecationWarning."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        warn_molecule_deprecated()
        warn_molecule_deprecated()

    assert len(caught) == 1
    assert issubclass(caught[0].category, DeprecationWarning)
    assert MOLECULE_DEPRECATION in str(caught[0].message)


@pytest.mark.parametrize(
    "args",
    (
        ["--molecule"],
        ["--molecule_base_config=/tmp/base.yml"],
        ["--molecule-unavailable-driver=skip"],
        ["--skip-no-git-change=HEAD~1"],
    ),
)
def test_molecule_cli_options_warn(args: list[str]) -> None:
    """Deprecated molecule CLI options should warn during conftest load.

    Args:
        args: CLI args that should trigger the molecule deprecation warning.
    """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        pytest_load_initial_conftests(args)

    molecule_warnings = [w for w in caught if MOLECULE_DEPRECATION in str(w.message)]
    assert len(molecule_warnings) == 1
    assert issubclass(molecule_warnings[0].category, DeprecationWarning)


def _write_molecule_yml(tmp_path: Path, data: dict) -> Path:  # type: ignore[type-arg]
    """Write a molecule.yml under tmp_path/molecule/default.

    Args:
        tmp_path: Temporary directory root
        data: YAML content for molecule.yml

    Returns:
        Path to molecule.yml
    """
    scenario = tmp_path / "molecule" / "default"
    scenario.mkdir(parents=True, exist_ok=True)
    path = scenario / "molecule.yml"
    path.write_text(yaml.dump(data), encoding="utf-8")
    return path


def _make_parent(config: MagicMock, path: Path) -> MagicMock:
    """Build a parent mock suitable for MoleculeItem/File construction.

    Returns:
        A MagicMock parent with config/path/session attributes set.
    """
    parent = MagicMock()
    parent.config = config
    parent.path = path
    parent.nodeid = "node"
    parent.session = MagicMock()
    parent.session.config = config
    return parent


def test_molecule_pytest_configure_registers_markers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """molecule_pytest_configure should register driver/molecule markers."""
    config = MagicMock()
    config._metadata = {"Packages": {}}
    config.option = MagicMock()
    added: list[str] = []
    config.addinivalue_line = lambda _section, line: added.append(line)

    monkeypatch.setattr(sys, "platform", "darwin")

    with (
        patch.dict("sys.modules", {"molecule": MagicMock(), "molecule.api": MagicMock()}),
        patch("molecule.api.drivers", return_value=["default", "docker"]),
    ):
        molecule_pytest_configure(config)

    assert config.option.molecule["default"]["available"] is True
    assert any("no_driver:" in line for line in added)
    assert any(line.startswith("molecule:") for line in added)


def test_molecule_pytest_configure_selinux_import_error(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Cover the selinux ImportError branch on linux with selinux config present."""
    config = MagicMock()
    config._metadata = {"Packages": {}}
    config.option = MagicMock()
    config.addinivalue_line = MagicMock()

    monkeypatch.setattr(sys, "platform", "linux")

    import builtins

    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "selinux":
            msg = "no selinux"
            raise ImportError(msg)
        return real_import(name, *args, **kwargs)

    with (
        patch.dict("sys.modules", {"molecule": MagicMock(), "molecule.api": MagicMock()}),
        patch("molecule.api.drivers", return_value=[]),
        patch.object(Path, "is_file", return_value=True),
        patch("builtins.__import__", side_effect=fake_import),
        caplog.at_level(logging.ERROR),
    ):
        molecule_pytest_configure(config)

    assert "libselinux" in caplog.text


def test_molecule_file_collect_from_parent(tmp_path: Path) -> None:
    """MoleculeFile.collect should yield a MoleculeItem via from_parent."""
    path = _write_molecule_yml(tmp_path, {"driver": {"name": "default"}})
    mol_file = MagicMock(spec=MoleculeFile)
    mol_file.path = path

    with patch.object(MoleculeItem, "from_parent", return_value=MagicMock()) as mock_fp:
        items = list(MoleculeFile.collect(mol_file))

    assert len(items) == 1
    mock_fp.assert_called_once()


def test_molecule_file_collect_legacy_constructor(tmp_path: Path) -> None:
    """Cover the else branch when from_parent is unavailable."""
    path = _write_molecule_yml(tmp_path, {"driver": {"name": "default"}})
    mol_file = MagicMock(spec=MoleculeFile)
    mol_file.path = path
    fake_item = MagicMock()

    real_hasattr = hasattr

    def fake_hasattr(obj: object, name: str) -> bool:
        if name == "from_parent":
            return False
        return real_hasattr(obj, name)

    with (
        patch("builtins.hasattr", fake_hasattr),
        patch("pytest_ansible.molecule.MoleculeItem", return_value=fake_item) as mock_cls,
    ):
        items = list(MoleculeFile.collect(mol_file))

    assert items == [fake_item]
    mock_cls.assert_called_once()


def test_molecule_file_str(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MoleculeFile.__str__ returns path relative to cwd."""
    rel = Path("relative/molecule.yml")
    full = tmp_path / rel
    full.parent.mkdir(parents=True)
    full.write_text("---\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    mol_file = object.__new__(MoleculeFile)
    mol_file.path = full
    assert str(mol_file) == str(rel)


def test_molecule_item_init_markers_and_str(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cover MoleculeItem.__init__ marker paths, __str__, and reportinfo."""
    path = _write_molecule_yml(
        tmp_path,
        {
            "driver": {"name": "default"},
            "platforms": [{"name": "instance"}],
            "markers": ["xfail", "skip"],
        },
    )
    config = MagicMock()
    config.option.molecule = {"default": {"available": True}}
    config.option.molecule_unavailable_driver = None
    config.addinivalue_line = MagicMock()
    parent = _make_parent(config, path)
    monkeypatch.chdir(tmp_path)

    with patch.object(MoleculeItem, "add_marker", MagicMock()) as mock_add_marker:
        item = MoleculeItem._create("test0", parent)

    assert item.molecule_driver == "default"
    assert str(item) == "test0[default]"
    assert item.reportinfo() == (path, 0, "use_case: test0")
    # xfail + skip + platform + molecule + driver markers
    assert mock_add_marker.call_count >= 4  # noqa: PLR2004


def test_molecule_item_global_config_and_unavailable_driver(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cover global config merge and unavailable-driver marker."""
    global_cfg = tmp_path / ".config" / "molecule" / "config.yml"
    global_cfg.parent.mkdir(parents=True)
    global_cfg.write_text(yaml.dump({"driver": {"name": "docker"}}), encoding="utf-8")

    path = _write_molecule_yml(tmp_path, {"platforms": [{"name": "p1"}]})
    config = MagicMock()
    config.option.molecule = {"docker": {"available": False}}
    config.option.molecule_unavailable_driver = "skip"
    config.addinivalue_line = MagicMock()
    parent = _make_parent(config, path)
    monkeypatch.chdir(tmp_path)

    with patch.object(MoleculeItem, "add_marker", MagicMock()) as mock_add_marker:
        item = MoleculeItem._create("test1", parent)

    assert item.molecule_driver == "docker"
    mock_add_marker.assert_any_call("skip")


def test_molecule_item_yaml_loader_empty(tmp_path: Path) -> None:
    """yaml_loader should return {} for empty YAML documents."""
    empty = tmp_path / "empty.yml"
    empty.write_text("", encoding="utf-8")
    item = MoleculeItem.__new__(MoleculeItem)
    assert item.yaml_loader(str(empty)) == {}


def test_molecule_item_runtest_disabled(tmp_path: Path) -> None:
    """Runtest should skip when --molecule is disabled."""
    path = _write_molecule_yml(tmp_path, {"driver": {"name": "default"}})
    item = MoleculeItem.__new__(MoleculeItem)
    item.path = path
    item.config = MagicMock()
    item.config.option.molecule_base_config = None
    item.config.option.skip_no_git_change = None
    item.config.getoption = MagicMock(return_value=False)

    with pytest.raises(pytest.skip.Exception, match="Molecule tests are disabled"):
        MoleculeItem.runtest(item)


def test_molecule_item_runtest_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Runtest should run molecule and succeed on returncode 0."""
    path = _write_molecule_yml(tmp_path, {"driver": {"name": "default"}})
    item = MoleculeItem.__new__(MoleculeItem)
    item.path = path
    item.config = MagicMock()
    item.config.option.molecule_base_config = "/tmp/base.yml"  # noqa: S108
    item.config.option.skip_no_git_change = None
    item.config.getoption = MagicMock(return_value=True)
    monkeypatch.setenv("MOLECULE_OPTS", "--debug")

    proc = MagicMock()
    proc.stdout = io.StringIO("ok\n")
    proc.returncode = 0
    proc.__enter__ = MagicMock(return_value=proc)
    proc.__exit__ = MagicMock(return_value=False)

    with patch("pytest_ansible.molecule.subprocess.Popen", return_value=proc) as mock_popen:
        MoleculeItem.runtest(item)

    cmd = mock_popen.call_args[0][0]
    assert "--base-config" in cmd
    assert "--debug" in cmd


def test_molecule_item_runtest_failure(tmp_path: Path) -> None:
    """Runtest should fail when molecule returns non-zero."""
    path = _write_molecule_yml(tmp_path, {"driver": {"name": "default"}})
    item = MoleculeItem.__new__(MoleculeItem)
    item.path = path
    item.config = MagicMock()
    item.config.option.molecule_base_config = None
    item.config.option.skip_no_git_change = None
    item.config.getoption = MagicMock(return_value=True)

    proc = MagicMock()
    proc.stdout = io.StringIO("boom\n")
    proc.returncode = 2
    proc.__enter__ = MagicMock(return_value=proc)
    proc.__exit__ = MagicMock(return_value=False)

    with (
        patch("pytest_ansible.molecule.subprocess.Popen", return_value=proc),
        pytest.raises(pytest.fail.Exception, match="Error code 2"),
    ):
        MoleculeItem.runtest(item)


def test_molecule_item_runtest_skip_no_git_change(tmp_path: Path) -> None:
    """Runtest should skip when git diff reports no changes."""
    path = _write_molecule_yml(tmp_path, {"driver": {"name": "default"}})
    item = MoleculeItem.__new__(MoleculeItem)
    item.path = path
    item.config = MagicMock()
    item.config.option.molecule_base_config = None
    item.config.option.skip_no_git_change = "HEAD~1"
    item.config.getoption = MagicMock(return_value=True)

    git_proc = MagicMock()
    git_proc.stdout = io.StringIO("")
    git_proc.__enter__ = MagicMock(return_value=git_proc)
    git_proc.__exit__ = MagicMock(return_value=False)

    with (
        patch("pytest_ansible.molecule.subprocess.Popen", return_value=git_proc),
        pytest.raises(pytest.skip.Exception, match="No change in role"),
    ):
        MoleculeItem.runtest(item)


def test_molecule_exception_error() -> None:
    """MoleculeExceptionError should be a regular Exception subclass.

    Raises:
        MoleculeExceptionError: Always, to assert the exception type.
    """
    msg = "boom"
    with pytest.raises(MoleculeExceptionError):
        raise MoleculeExceptionError(msg)


def test_molecule_item_runtest_with_git_changes(tmp_path: Path) -> None:
    """Runtest continues when git diff reports changes."""
    path = _write_molecule_yml(tmp_path, {"driver": {"name": "default"}})
    item = MoleculeItem.__new__(MoleculeItem)
    item.path = path
    item.config = MagicMock()
    item.config.option.molecule_base_config = None
    item.config.option.skip_no_git_change = "HEAD~1"
    item.config.getoption = MagicMock(return_value=True)

    git_proc = MagicMock()
    git_proc.stdout = io.StringIO("M roles/foo/tasks/main.yml\n")
    git_proc.__enter__ = MagicMock(return_value=git_proc)
    git_proc.__exit__ = MagicMock(return_value=False)

    mol_proc = MagicMock()
    mol_proc.stdout = io.StringIO("ok\n")
    mol_proc.returncode = 0
    mol_proc.__enter__ = MagicMock(return_value=mol_proc)
    mol_proc.__exit__ = MagicMock(return_value=False)

    with patch(
        "pytest_ansible.molecule.subprocess.Popen",
        side_effect=[git_proc, mol_proc],
    ):
        MoleculeItem.runtest(item)


def test_molecule_scenario_test(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MoleculeScenario.test runs molecule with optional MOLECULE_OPTS."""
    scenario = MoleculeScenario(
        name="default",
        parent_directory=tmp_path,
        test_id="role-default",
    )
    monkeypatch.setenv("MOLECULE_OPTS", "--destroy=always")
    completed = MagicMock()

    with (
        patch("pytest_ansible.molecule.warn_molecule_deprecated"),
        patch("pytest_ansible.molecule.subprocess.run", return_value=completed) as mock_run,
    ):
        result = scenario.test()

    assert result is completed
    args = mock_run.call_args.kwargs["args"]
    assert "default" in args
    assert "--destroy=always" in args


def test_molecule_scenario_test_without_opts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MoleculeScenario.test without MOLECULE_OPTS covers the unset branch."""
    scenario = MoleculeScenario(
        name="default",
        parent_directory=tmp_path,
        test_id="role-default",
    )
    monkeypatch.delenv("MOLECULE_OPTS", raising=False)

    with (
        patch("pytest_ansible.molecule.warn_molecule_deprecated"),
        patch("pytest_ansible.molecule.subprocess.run", return_value=MagicMock()) as mock_run,
    ):
        scenario.test()

    args = mock_run.call_args.kwargs["args"]
    assert args == [sys.executable, "-m", "molecule", "test", "-s", "default"]
