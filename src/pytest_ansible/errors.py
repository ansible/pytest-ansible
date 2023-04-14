"""Defines pytest-ansible exception classes."""

import ansible.errors


class AnsibleNoHostsMatch(ansible.errors.AnsibleError):
    """Sub-class AnsibleError when no hosts match."""


class AnsibleConnectionFailure(ansible.errors.AnsibleError):
    """Sub-class AnsibleError when connection failures occur."""

    def __init__(self, msg, dark=None, contacted=None) -> None:
        """Initialize connection error class."""
        super().__init__(msg)
        self.contacted = contacted
        self.dark = dark


class AnsibleModuleError(ansible.errors.AnsibleError):
    """Sub-class AnsibleError when module failures occur."""
