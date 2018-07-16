"""Defines pytest-ansible exception classes."""

import ansible.errors


class AnsibleNoHostsMatch(ansible.errors.AnsibleError):

    """Sub-class AnsibleError when no hosts match."""

    pass


class AnsibleConnectionFailure(ansible.errors.AnsibleError):

    """Sub-class AnsibleError when connection failures occur."""

    def __init__(self, msg, dark=None, contacted=None):
        """Initialize connection error class."""
        super(AnsibleConnectionFailure, self).__init__(msg)
        self.contacted = contacted
        self.dark = dark


class AnsibleModuleError(ansible.errors.AnsibleError):

    """Sub-class AnsibleError when module failures occur."""

    pass
