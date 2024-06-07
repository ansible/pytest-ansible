"""Tests specific to the molecule plugin functionality."""

from __future__ import annotations

import os
import subprocess
import sys

from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from pytest_ansible.molecule import MoleculeScenario


def test_molecule_collect() -> None:
    """Test pytest collection of molecule scenarios."""
    try:
        proc = subprocess.run(
            "pytest --molecule --collect-only",  # noqa: S607
            capture_output=True,
            shell=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        pytest.fail(exc.stderr)

    assert proc.returncode == 0
    assert "test1[default]" in proc.stdout


def test_molecule_disabled() -> None:
    """Ensure the lack of --molecule disables molecule support."""
    proc = subprocess.run(
        f"{sys.executable} -m pytest tests/fixtures/molecule/default/molecule.yml",
        capture_output=True,
        check=False,
        env={"PATH": os.environ["PATH"]},
        shell=True,
        text=True,
    )
    assert proc.returncode == 4  # noqa: PLR2004
    # First check is for pytest 7 behavior, second for pytest >=8
    assert "ERROR: found no collectors" in proc.stderr or "ERROR: not found" in proc.stderr


def test_molecule_runtest() -> None:
    """Test running the molecule scenario via pytest."""
    try:
        proc = subprocess.run(
            f"{sys.executable} -m pytest -v --molecule tests/fixtures/molecule/default/molecule.yml",  # noqa: E501
            capture_output=True,
            check=True,
            env={"PATH": os.environ["PATH"]},
            shell=True,
            text=True,
        )
        assert proc.returncode == 0
        assert "collected 1 item" in proc.stdout
        assert "tests/fixtures/molecule/default/molecule.yml::test" in proc.stdout
        assert "1 passed" in proc.stdout

    except subprocess.CalledProcessError as exc:
        pytest.fail(exc.stderr)


def test_molecule_fixture(molecule_scenario: MoleculeScenario) -> None:
    """Test the scenario fixture.

    :param molecule_scenario: One scenario
    """
    assert molecule_scenario.test_id in ["fixtures-default", "extensions-default"]
    assert molecule_scenario.name == "default"
    molecule_scenario.test()
