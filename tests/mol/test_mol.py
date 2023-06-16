import os
import subprocess
from unittest.mock import Mock

import pytest

try:
    from pytest_ansible.molecule import MoleculeFile, MoleculeItem
except ModuleNotFoundError:
    MoleculeItem = None
    MoleculeFile = None


class TestMoleculeItem:
    "Perform run test"

    @pytest.fixture()
    def test_run(self, mocker):  # noqa: PT004
        mocker.patch("MoleculeItem.path", Mock())
        mocker.patch("MoleculeItem.config.option.molecule_base_config", None)
        mocker.patch("MoleculeItem.config.option.skip_no_git_change", None)
        mocker.patch("subprocess.Popen")
        mocker.patch("MoleculeItem.config.getoption", lambda x: True)  # noqa: PT008

        molecule_item = MoleculeItem("test", None)
        molecule_item.runtest()
        proc = subprocess.run(
            "pytest pytest-ansible/molecule/default/molecule.yml -v",
            shell=True,
            check=True,
            cwd=os.path.abspath(os.path.join(molecule_item.path.parent, "../..")),
            capture_output=True,
        )
        assert proc.returncode == 0
        output = proc.stdout.decode("utf-8")
        assert "collected 1 item" in output
        assert "pytest-ansible/molecule/default/molecule.yml::test" in output
        assert "1 passed" in output


class TestMoleculeFile:
    "Test Generator to collect the test"

    @pytest.fixture()
    def test_collect(self, mocker):  # noqa: PT004
        mocker.patch("MoleculeItem.from_parent")
        mocker.patch("MoleculeItem.__init__")
        mocker.patch("MoleculeItem.__str__")
        mocker.patch("MoleculeFile.path", Mock())

        # Test when MoleculeItem.from_parent exists
        MoleculeItem.from_parent.return_value = "mocked_item"
        molecule_file = MoleculeFile()
        items = list(molecule_file.collect())
        assert items == ["mocked_item"]

        # Test when MoleculeItem.from_parent does not exist
        MoleculeItem.from_parent.side_effect = AttributeError
        MoleculeItem.return_value = "mocked_item"
        molecule_file = MoleculeFile()
        items = list(molecule_file.collect())
        assert items == ["mocked_item"]

        proc = subprocess.run(
            "pytest --collect-only",
            shell=True,
            check=True,
            capture_output=True,
        )
        assert proc.returncode == 0
        output = proc.stdout.decode("utf-8")
        assert "1 test collected" in output
        assert "test[delegated]" in output

    @pytest.fixture()
    def _test_str(self, mocker):
        mocker.patch("MoleculeFile.path", Mock(return_value="mock/path"))
        mocker.patch("os.getcwd", Mock(return_value="mock/cwd"))
        molecule_file = MoleculeFile()
        assert str(molecule_file) == "mock/path"
        assert str(molecule_file) == "mock/path"
        assert str(molecule_file) == "mock/path"
        assert str(molecule_file) == "mock/path"
