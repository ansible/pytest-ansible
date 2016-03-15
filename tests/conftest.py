import ansible
import pytest
from pkg_resources import parse_version


pytest_plugins = 'pytester',

# Indicate whether ansible-2.* is available
# requires_ansible_v1 = pytest.mark.skipif(parse_version(ansible.__version__) >= parse_version('2.0.0'),
#                                          reason="requires ansible-1.*")
# requires_ansible_v2 = pytest.mark.skipif(parse_version(ansible.__version__) < parse_version('2.0.0'),
#                                          reason="requires ansible-2.*")


def pytest_runtest_setup(item):
    # Conditionally skip tests that are pinned to a specific ansible version
    if isinstance(item, item.Function):
        has_ansible_v1 = parse_version(ansible.__version__) < parse_version('2.0.0')
        if item.get_marker('requires_ansible_v1') and not has_ansible_v1:
            pytest.skip("requires < ansible-2.*")
        if item.get_marker('requires_ansible_v2') and has_ansible_v1:
            pytest.skip("requires >= ansible-2.*")


class PyTestOption(object):

    def __init__(self, config, testdir):
        self.config = config

        # Create inventory file
        self.inventory = testdir.makefile('.ini', inventory='''
            [local]
            localhost ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.2 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.3 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.4 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'
            127.0.0.5 ansible_connection=local ansible_python_interpreter='/usr/bin/env python'

            [unreachable]
            unreachable-host-1.example.com
            unreachable-host-2.example.com
            unreachable-host-3.example.com
        ''')

        # Create ansible.cfg file
        # self.ansible_cfg = testdir.makefile('.cfg', ansible='''[ssh_connection]\ncontrol_path = %(directory)s/%%h-%%r''')

    @property
    def args(self):
        args = list()
        args.append('--tb')
        args.append('native')
        return args


@pytest.fixture()
def option(request, testdir):
    '''Returns an instance of PyTestOption to help tests pass parameters and
    use a common inventory file.
    '''
    return PyTestOption(request.config, testdir)
