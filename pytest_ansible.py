'''
A pytest plugin that enables the use of ansible
'''

import os
import py
import pytest
import subprocess
import requests
import pipes
import logging
import ansible.runner
import ansible.inventory
from urlparse import urlparse

__version__ = '1.0'
__author__ = 'James Laska'
__author_email__ = 'jlaska@ansible.com'

log = logging.getLogger(__name__)


def pytest_addoption(parser):
    group = parser.getgroup('ansible', 'ansible')
    group.addoption('--ansible-inventory',
                     action='store',
                     dest='ansible_inventory',
                     default='/etc/ansible/hosts',
                     metavar='ANSIBLE-INVENTORY',
                     help='ansible inventory file URI')

    group.addoption('--ansible-host-pattern',
                     action='store',
                     dest='ansible_host_pattern',
                     default=None,
                     metavar='ANSIBLE-HOST-PATTERN',
                     help='Specify ansible host pattern')


def pytest_configure(config):
    '''
    Sanitize --ansible-* parameters.
    Ensure --ansible-inventory references a valid file. If a remote URL is
    used, download the file locally.
    '''

    # Yuck, is there a better way to benefit from pytest_tmpdir?
    tmpdir = config.pluginmanager.getplugin("tmpdir").TempdirHandler(config).getbasetemp()

    # Sanitize ansible_hostname
    ansible_hostname = config.getvalue('ansible_host_pattern')
    # If using pytest_mozwebqa, just use the the value of --baseurl
    if ansible_hostname is None and hasattr(config.option, 'base_url'):
        # attempt to use --baseurl as ansible_host_pattern
        ansible_hostname = urlparse(config.getvalue('base_url')).hostname
    if ansible_hostname is None:
        py.test.exit("No ansible host pattern provided (--ansible-host-pattern)")

    # Sanitize ansible_inventory
    ansible_inventory = config.getvalue('ansible_inventory')
    if not config.option.collectonly:

        # Convert file URL to absolute path (file:///path/to/file.ini ->
        # /path/to/file.ini)
        if ansible_inventory.startswith('file:///'):
            ansible_inventory = urlparse(ansible_inventory).path

        # Open inventory file (download if necessary)
        if os.path.exists(ansible_inventory):
            fd = open(ansible_inventory, 'r')
            inventory_data = fd.read()
        elif '://' in ansible_inventory:
            try:
                fd = requests.get(ansible_inventory)
            except Exception, e:
                py.test.exit("Unable to download ansible inventory file - %s" % e)
            inventory_data = fd.text
        else:
            py.test.exit("Ansible inventory file not found: %s" % ansible_inventory)

        # Create new inventory in tmpdir
        local_inventory = tmpdir.mkdir("ansible").join("inventory.ini").open('a+')
        # Remember the local filename
        ansible_inventory = local_inventory.name
        config.option.ansible_inventory = local_inventory.name

        # Ansible inventory files support host aliasing
        # (http://www.ansibleworks.com/docs/intro_inventory.html#id10)
        # If host aliasing is used, the <alias> likely won't match the
        # base_url.  The following will re-write the provided inventory
        # file, removing the alias.
        # For example, an inventory pattern as noted below:
        #   <alias> ansible_ssh_host=<fqdn> foo=bar
        # Becomes:
        #   <fqdn> ansible_ssh_host=<fqdn> foo=bar # <alias>
        for line in inventory_data.split('\n'):
            if ansible_hostname in line and not line.startswith(ansible_hostname):
                (alias, remainder) = line.split(' ', 1)
                line = "%s %s # %s" % (ansible_hostname, remainder, alias)
            local_inventory.write(line + '\n')


@pytest.fixture(scope='session')
def ansible_facts(request, ansible_runner):
    '''
    Return ansible_facts dictionary
    '''
    results = ansible_runner.setup()
    if isinstance(results, dict):
        return results.get('ansible_facts', {})
    else:
        return dict()


# def pytest_funcarg__ansible_runner(request):
@pytest.fixture(scope='session')
def ansible_runner(request):
    '''
    Return initialized ansibleWrapper
    '''
    inventory = request.config.getvalue('ansible_inventory')
    hostname = urlparse(request.config.getvalue('base_url')).hostname
    return AnsibleWrapper(inventory, hostname)


class AnsibleWrapper(object):
    '''
    Wrapper around ansible.runner.Runner()

    == Examples ==
    aw = AnsibleWrapper('/path/to/inventory')
    results = aw.command('mkdir /var/lib/testing', creates='/var/lib/testing')

    results = aw.git(repo='https://github.com/ansible/ansible.git', dest='/tmp/ansible')
    '''

    def __init__(self, inventory, pattern='all'):
        self.inventory = inventory
        self.pattern = pattern
        self.module_name = None

    def __getattr__(self, name):
        self.module_name = name
        return self.ansible_runner
        # return self.subprocess_runner

    def ansible_runner(self, *args, **kwargs):
        '''
        The API provided by ansible is not intended as a public API.
        Therefore, the following approach isn't guarrunteed to work.  Instead,
        use subprocess_runner().
        '''
        inventory = ansible.inventory.Inventory(self.inventory)

        # Assemble module argument string
        # module_args = [pipes.quote(s) for s in args]
        # if kwargs:
        #     module_args += ["%s=%s" % i for i in kwargs.items()]
        # module_args = ' '.join(module_args)
        module_args = []
        if args:
            module_args += list(args)

        # if kwargs:
        #     module_args += ["%s=%s" % (k, pipes.quote(v)) for k,v in kwargs.items()]

        module_args = ' '.join(module_args)

        # Log the module and parameters
        log.debug("[%s] %s: %s, %s" % (self.pattern, self.module_name, module_args, kwargs))

        runner = ansible.runner.Runner(
            inventory=inventory,
            pattern=self.pattern,
            module_name=self.module_name,
            module_args=module_args,
            complex_args=kwargs,
            sudo=True,)
        result = runner.run()

        # FIXME - improve result output logging
        log.debug(result)

        # FIXME - should command failures raise an exception, or return?
        # If we choose to raise, callers will need to adapt accordingly
        # Catch any failures in the response
        # for host in result['contacted'].values():
        #     if 'failed' in host or host.get('rc', 0) != 0:
        #         raise Exception("Command failed: %s" % self.module_name, result)

        # Raise exception if host was unreachable
        if result['dark']:
            raise Exception("Host unreachable: %s" % self.module_name, result['dark'])

        # Success!
        return result['contacted'][self.pattern]

    def subprocess_runner(self, *args, **kwargs):
        '''
        Build argument string and run `ansible-playbook ...`
        Returns: stdout
        '''

        # Disable host key checking
        # (http://www.ansibleworks.com/docs/intro_getting_started.html#host-key-checking)
        # os.environ['ANSIBLE_HOST_KEY_CHECKING'] = 'False'

        # Build module arguments
        module_args = []
        if args:
            module_args += list(args)
        if kwargs:
            module_args += ["%s=%s" % (k, pipes.quote(v)) for k, v in kwargs.items()]

        # Build command
        cmd = ['ansible', '-vvvv', self.pattern, '-m', self.module_name, '-i', self.inventory, '--sudo']
        if module_args:
            cmd += ['-a', ' '.join(module_args)]

        popen = subprocess.Popen(cmd, shell=False, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        stdout = popen.communicate()[0]
        if popen.returncode:
            raise Exception("Command failed (%s): %s\n%s" % (popen.returncode, cmd, stdout))
        # Drop the first line of output ... it's just a status line
        stdout = '\n'.join(stdout.split('\n')[1:])
        return (popen.returncode, stdout)
