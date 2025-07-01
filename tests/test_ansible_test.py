"""Checks compatibility with ansible-test."""

from __future__ import annotations

import subprocess  # noqa: S404


def test_ansible_test() -> None:
    """Test for params."""
    proc = subprocess.run(
        "ansible-test units --target-python default",  # noqa: S607
        shell=True,
        capture_output=True,
        cwd="tests/fixtures/ansible_collections/test/test",
        check=False,
    )
    assert proc.returncode == 0
