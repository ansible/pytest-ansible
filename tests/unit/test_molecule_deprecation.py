"""Tests for molecule-via-pytest deprecation warnings."""

from __future__ import annotations

import warnings

import pytest

from pytest_ansible import molecule as molecule_mod
from pytest_ansible.molecule import MOLECULE_DEPRECATION, warn_molecule_deprecated
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
