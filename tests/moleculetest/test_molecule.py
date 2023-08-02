"""Tests specific to the molecule plugin functionality."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

try:
    from pytest_ansible.molecule import MoleculeFile, MoleculeItem
except ModuleNotFoundError:
    MoleculeFile = None
    MoleculeItem = None


def test_molecule_collect(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test collecting a molecule.yml file.

    :param monkeypatch: The pytest monkeypatch fixture
    :param tmp_path: The pytest tmp_path fixture
    :param caplog: The pytest caplog fixture
    """
    caplog.set_level(logging.DEBUG)

    # Create a temporary molecule file for testing
    molecule_file_path = (
        tmp_path / "pytest-ansible" / "molecule" / "default" / "molecule.yml"
    )
    molecule_file_path.parent.mkdir(parents=True, exist_ok=True)
    molecule_file_path.write_text("test content")

    # Create the MoleculeFile object for the temporary file
    molecule_file = MoleculeFile(molecule_file_path, parent=None)

    # Mock MoleculeItem object for testing
    mocked_item = MagicMock()
    monkeypatch.setattr(
        MoleculeItem,
        "from_parent",
        MagicMock(return_value=mocked_item),
    )

    # Call the collect() method and convert the generator into a list to check its content
    collected_items = list(molecule_file.collect())

    # Clean up the temporary file and directory
    molecule_file_path.unlink()
    molecule_file_path.parent.rmdir()

    try:
        proc = subprocess.run(
            "pytest --collect-only",
            capture_output=True,
            shell=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print(exc.stdout)
        print(exc.stderr)
        pytest.fail(exc.stderr)

    assert proc.returncode == 0
    output = proc.stdout.decode("utf-8")
    assert "1 test collected" in output
    assert "test[delegated]" in output
    assert len(collected_items) == 1
    assert collected_items[0] == mocked_item


def test_molecule_runtest(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.LogCaptureFixture,
) -> None:
    """Test running the file.

    :param monkeypatch: The pytest monkeypatch fixture
    :param tmp_path: The pytest tmp_path fixture
    :param capsys: The pytest capsys fixture
    """
    # Test runtest() function in MoleculeItem
    # Mock necessary attributes and environment variables
    monkeypatch.setattr(subprocess, "Popen", MagicMock())
    monkeypatch.setenv("MOLECULE_OPTS", "--driver-name mock_driver")
    monkeypatch.setattr(sys, "executable", "/path/to/python")
    monkeypatch.setattr(os, "getcwd", MagicMock(return_value="/path/to"))

    molecule_item = MoleculeItem("test", parent=None)

    # Run the runtest() function
    molecule_item.runtest()

    proc = subprocess.run(
        f"{sys.executable} -m pytest molecule.yml -v",
        shell=True,
        check=True,
        cwd="/home/ruchi/pytest-ansible/molecule/default/",
        capture_output=True,
    )
    assert proc.returncode == 0
    output = proc.stdout.decode("utf-8")
    assert "collected 1 item" in output
    assert "pytest-ansible/molecule/default/molecule.yml::test" in output
    assert "1 passed" in output

    # Capture the printed output and check if the command is correctly formed
    captured = capsys.readouterr()
    assert (
        captured.out.strip()
        == "running: python -m molecule test -s scenario --driver-name mock_driver"
    )
