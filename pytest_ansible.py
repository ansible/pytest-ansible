import os
import py
import pytest
import json
import logging
import ansible.runner
import ansible.constants
import ansible.inventory
import ansible.errors
import ansible.utils
from urlparse import urlparse

__version__ = '1.0'
__author__ = "James Laska"
__author_email__ = "<jlaska@ansible.com>"

log = logging.getLogger(__name__)

# ansible.utils.VERBOSITY = 4


class AnsibleNoHostsMatch(ansible.errors.AnsibleError):
    pass


def pytest_addoption(parser):
    '''Add options to control ansible.'''

    def increment_debug(option, opt, value, parser):
        ansible.utils.VERBOSITY += 1

    group = parser.getgroup('pytest-ansible')
    group.addoption('--ansible-inventory',
                    action='store',
                    dest='ansible_inventory',
                    default=ansible.constants.DEFAULT_HOST_LIST,
                    metavar='ANSIBLE_INVENTORY',
                    help='ansible inventory file URI (default: %default)')
    group.addoption('--ansible-host-pattern',
                    action='store',
                    dest='ansible_host_pattern',
                    default='all',
                    metavar='ANSIBLE_HOST_PATTERN',
                    help='ansible host pattern (default: %default)')
    group.addoption('--ansible-user',
                    action='store',
                    dest='ansible_user',
                    default=ansible.constants.DEFAULT_REMOTE_USER,
                    help='connect as this user (default: %default)')
    group.addoption('--ansible-sudo',
                    action='store_true',
                    dest='ansible_sudo',
                    default=ansible.constants.DEFAULT_SUDO,
                    help='run operations with sudo [nopasswd] (default: %default)')
    group.addoption('--ansible-sudo-user',
                    action='store',
                    dest='ansible_sudo_user',
                    default='root',
                    help='desired sudo user (default: %default)')


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

    # Verify --ansible-host-pattern was provided
    if not (config.option.help or config.option.showfixtures):
        if ansible_hostname is None:
            print("ERROR: Missing required parameter --ansible-host-pattern")
            py.test.exit("Missing required parameter --ansible-host-pattern")

    # Sanitize ansible_inventory
    ansible_inventory = config.getvalue('ansible_inventory')
    if not config.option.collectonly:
        '''
        Do some validation with the host_pattern?
        '''
        if False:
            import requests

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


class AnsibleModule(object):
    '''
    Wrapper around ansible.runner.Runner()

    == Examples ==
    aw = AnsibleModule('/path/to/inventory')
    results = aw.command('mkdir /var/lib/testing', creates='/var/lib/testing')

    results = aw.git(repo='https://github.com/ansible/ansible.git', dest='/tmp/ansible')
    '''

    def __init__(self, inventory, pattern, **kwargs):
        self.inventory = inventory
        self.pattern = pattern
        self.options = kwargs
        self.module_name = None

    def __getattr__(self, name):
        self.module_name = name
        return self.__run

        # try:
        #     return self.__run
        # except ansible.errors.AnsibleConnectionFailed, e:
        #     result = dict(failed=True, msg="FAILED: %s" % str(e))
        #     return ansible.runner.return_data.ReturnData(host=host, comm_ok=False, result=result)

    def __run(self, *args, **kwargs):
        '''
        The API provided by ansible is not intended as a public API.
        '''
        # Initialize ansible inventory manage
        inventory_manager = ansible.inventory.Inventory(self.inventory)

        # Assemble module argument string
        module_args = list()
        if args:
            module_args += list(args)
        module_args = ' '.join(module_args)

        # Assert hosts matching the provided pattern exist
        log.debug("inventory_manager.list_hosts(%s)" % self.pattern)
        hosts = inventory_manager.list_hosts(self.pattern)
        if len(hosts) == 0:
            raise AnsibleNoHostsMatch("No hosts match:'%s'" % self.pattern)

        # Log the module and parameters
        log.debug("[%s] %s: %s, %s" % (self.pattern, self.module_name, module_args, kwargs))

        # Build module runner object
        runner = ansible.runner.Runner(
            inventory=inventory_manager,
            pattern=self.pattern,
            module_name=self.module_name,
            module_args=module_args,
            complex_args=kwargs,
            sudo=self.options.get('sudo'),
            sudo_user=self.options.get('sudo_user'),)

        # Run the module
        results = runner.run()

        # FIXME - improve result output logging
        log.debug(results)

        # FIXME - should command failures raise an exception, or return?
        # If we choose to raise, callers will need to adapt accordingly
        # Catch any failures in the response
        # for host in results['contacted'].values():
        #     if 'failed' in host or host.get('rc', 0) != 0:
        #         raise Exception("Command failed: %s" % self.module_name, results)

        # Raise exception if host(s) unreachable
        # FIXME - if multiple hosts were involved, should an exception be raised?
        if results['dark']:
            raise ansible.errors.AnsibleConnectionFailed("Host unreachable: %s" % json.dumps(results['dark'], indent=2))

        # No hosts contacted
        if not results['contacted']:
            raise ansible.errors.AnsibleConnectionFailed("Provided hosts list is empty")

        # No matching host contacted
        if self.pattern not in inventory_manager.groups_list() and self.pattern not in results['contacted']:
            raise AnsibleNoHostsMatch("No hosts match:'%s'" % self.pattern)

        # Success!
        return results['contacted']
        # return results['contacted'][self.pattern]


@pytest.fixture(scope='function')
def ansible_module(request):
    '''
    Return initialized ansibleWrapper
    '''

    # Grab options from command-line
    inventory = request.config.getvalue('ansible_inventory')
    host_pattern = request.config.getvalue('ansible_host_pattern')
    sudo = request.config.getvalue('ansible_sudo')
    sudo_user = request.config.getvalue('ansible_sudo_user')

    # Override options from @pytest.mark.ansible
    ansible_args = getattr(request.function, 'ansible', None)
    if ansible_args:
        if 'inventory' in ansible_args.kwargs:
            inventory = ansible_args.kwargs['inventory']
        if 'host_pattern' in ansible_args.kwargs:
            host_pattern = ansible_args.kwargs['host_pattern']
        if 'sudo' in ansible_args.kwargs:
            sudo = ansible_args.kwargs['sudo']
        if 'sudo_user' in ansible_args.kwargs:
            sudo_user = ansible_args.kwargs['sudo_user']

    return AnsibleModule(inventory, host_pattern, sudo=sudo, sudo_user=sudo_user)


@pytest.fixture(scope='function')
def ansible_facts(request, ansible_module):
    '''
    Return ansible_facts dictionary
    '''
    results = ansible_module.setup()
    return results
