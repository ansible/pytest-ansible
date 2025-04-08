"""Functional tests for pytest-ansible."""

from __future__ import annotations

from typing import Any

import pytest


@pytest.mark.ansible(inventory="local,", connection="local", host_pattern="all")
def test_func(ansible_module: Any) -> None:  # noqa: ANN401
    """Sample test for ansible module.

    Args:
        ansible_module: The ansible module.
    """
    ansible_module.ping()
