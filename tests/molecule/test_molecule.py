"""Tests specific to the pytest-molecule plugin."""

from __future__ import annotations

import subprocess
from pathlib import Path

from pytest_ansible.molecule import MoleculeItem

FIXTURE_DIRECTORY = Path(__file__).resolve().parent / "fixtures"


def test_collect():
    # Create a mock pytest.File object representing a molecule file
    mock_molecule_file = MockMoleculeFile(
        "/home/ruchi/pytest-ansible/molecule/default/molecule.yml",
    )

    # Create an instance of MoleculeItem with the mock molecule file
    molecule_item = MoleculeItem("test", mock_molecule_file)

    # Call the collect() method of MoleculeItem and get the collected items
    collected_items = list(molecule_item.collect())

    # Run pytest with --collect-only and assert a molecule scenario is there
    proc = subprocess.run(
        "pytest --collect-only",
        shell=True,
        check=True,
        cwd=FIXTURE_DIRECTORY,
        capture_output=True,
    )

    # Assert that the collected items contain the MoleculeItem instance
    assert molecule_item in collected_items
    assert proc.returncode == 0
    output = proc.stdout.decode("utf-8")
    assert "1 test collected" in output
    assert "test[delegated]" in output


def test_run():
    # Create a mock pytest.File object representing a molecule file
    mock_molecule_file = MockMoleculeFile(
        "/home/ruchi/pytest-ansible/molecule/default/molecule.yml",
    )

    # Create an instance of MoleculeItem with the mock molecule file
    molecule_item = MoleculeItem("test", mock_molecule_file)
    # Patch the necessary dependencies
    proc = subprocess.run(
        "pytest /home/ruchi/pytest-ansible/molecule/default/molecule.yml -v",
        shell=True,
        check=True,
        cwd=FIXTURE_DIRECTORY,
        capture_output=True,
    )

    # Call the runtest() method of MoleculeItem
    molecule_item.runtest()
    output = proc.stdout.decode("utf-8")
    assert "collected 1 item" in output
    assert "test_scenario::lint" in output
    assert "test_scenario::dependency" in output
    assert "test_scenario::syntax" in output
    assert "test_scenario::create" in output
    assert "test_scenario::prepare" in output
    assert "test_scenario::converge" in output
    assert "test_scenario::verify" in output
    assert "1 passed" in output


class MockMoleculeFile:
    "Mock class for pytest.file"

    def __init__(self, path):
        self.path = path

    def collect(self):
        yield MockMoleculeItem()


class MockMoleculeItem:
    "Mock class for MoleculeItem"

    def __init__(self):
        self.name = "test"
        self.path = "/home/ruchi/pytest-ansible/molecule/default/molecule.yml"
