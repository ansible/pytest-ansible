import os
import subprocess
from unittest.mock import Mock, patch

import pytest
from pytest_mock import MockerFixture

try:
    from pytest_ansible.molecule import MoleculeFile, MoleculeItem
except ModuleNotFoundError:
    MoleculeItem = None
    MoleculeFile = None


def test_run(mocker: MockerFixture):  # noqa: PT004
    mocker.patch("pytest_ansible.molecule.MoleculeItem.path", Mock())
    mocker.patch("MoleculeItem.config.option.molecule_base_config", None)
    mocker.patch("MoleculeItem.config.option.skip_no_git_change", None)
    mocker.patch("subprocess.Popen")
    mocker.patch("MoleculeItem.config.getoption", return_value=True)

    with patch.object(Mock, "config"):
        molecule_item = MoleculeItem.from_parent(name="test", parent=Mock())
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

    # Add test result
    expected_output = "EXPECTED_OUTPUT"
    if output != expected_output:
        pytest.fail(
            f"Test output does not match the expected output.\n\n"
            f"Expected:\n{expected_output}\n\n"
            f"Actual:\n{output}",
        )


def test_collect(mocker: MockerFixture):
    mocker.patch("pytest_ansible.molecule.MoleculeItem.from_parent")
    mocker.patch("pytest_ansible.molecule.MoleculeItem.__init__")
    mocker.patch("pytest_ansible.molecule.MoleculeItem.__str__")
    mocker.patch("pytest_ansible.molecule.MoleculeFile.path", Mock())

    # Test when MoleculeItem.from_parent exists
    MoleculeItem.from_parent.return_value = "mocked_item"
    molecule_file = MoleculeFile()
    items = list(molecule_file.collect())
    assert items == ["mocked_item"]

    # Test when MoleculeItem.from_parent does not exist
    MoleculeItem.from_parent.side_effect = AttributeError
    mocker.patch.object(MoleculeItem, "__new__", return_value="mocked_item")

    molecule_file = MoleculeFile()
    items = list(molecule_file.collect())
    assert items == ["mocked_item"]

    mocker.patch("subprocess.run")
    subprocess.run.return_value = subprocess.CompletedProcess(
        args="pytest --collect-only",
        returncode=0,
        stdout=b"1 test collected\ntest[delegated]\n",
        stderr=b"",
    )

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


if __name__ == "__main__":
    pytest.main(["-v", __file__])
