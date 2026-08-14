"""Checks compatibility with ansible-test."""

from __future__ import annotations

import subprocess  # ruff: ignore[suspicious-subprocess-import]


def test_ansible_test() -> None:
    """Test for params."""
    proc = subprocess.run(
        "ansible-test units --target-python default",  # ruff: ignore[start-process-with-partial-path]
        shell=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd="tests/fixtures/ansible_collections/test/test",
        check=False,
    )
    assert proc.returncode == 0
