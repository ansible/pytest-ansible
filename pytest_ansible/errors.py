import ansible.errors


class AnsibleNoHostsMatch(ansible.errors.AnsibleError):
    pass


class AnsibleConnectionFailure(ansible.errors.AnsibleError):

    '''FIXME'''

    def __init__(self, msg, dark=None, contacted=None):
        super(AnsibleConnectionFailure, self).__init__(msg)
        self.contacted = contacted
        self.dark = dark


class AnsibleModuleError(ansible.errors.AnsibleError):
    pass
