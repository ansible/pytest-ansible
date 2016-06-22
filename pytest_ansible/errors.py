import ansible.errors


class AnsibleNoHostsMatch(ansible.errors.AnsibleError):
    pass


class AnsibleHostUnreachable(ansible.errors.AnsibleError):

    '''FIXME'''

    def __init__(self, msg, dark=None, contacted=None):
        super(AnsibleHostUnreachable, self).__init__(msg)
        self.contacted = contacted
        self.dark = dark

    @property
    def results(self):
        return (self.contacted, self.dark)


class AnsibleConnectionFailure(ansible.errors.AnsibleError):

    '''FIXME'''

    def __init__(self, msg, dark=None, contacted=None):
        super(AnsibleConnectionFailure, self).__init__(msg)
        self.contacted = contacted
        self.dark = dark

    @property
    def results(self):
        return (self.contacted, self.dark)


class AnsibleModuleError(ansible.errors.AnsibleError):
    pass
