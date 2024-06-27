"""Defines pytest-ansible exception classes."""

import ansible.errors


class AnsibleNoHostsMatch(ansible.errors.AnsibleError):  # type: ignore[misc]
    """Sub-class AnsibleError when no hosts match."""


class AnsibleConnectionFailure(ansible.errors.AnsibleError):  # type: ignore[misc]
    """Sub-class AnsibleError when connection failures occur."""

    def __init__(self, msg, dark=None, contacted=None) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001
        """Initialize connection error class."""
        super().__init__(msg)
        self.contacted = contacted
        self.dark = dark


class AnsibleModuleError(ansible.errors.AnsibleError):  # type: ignore[misc]
    """Sub-class AnsibleError when module failures occur."""
