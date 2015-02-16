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

__version__ = '1.1'
__author__ = "James Laska"
__author_email__ = "<jlaska@ansible.com>"

log = logging.getLogger(__name__)

# ansible.utils.VERBOSITY = 4


class AnsibleNoHostsMatch(ansible.errors.AnsibleError):
    pass


class AnsibleHostUnreachable(ansible.errors.AnsibleError):
    def __init__(self, msg, result=None):
        super(AnsibleHostUnreachable, self).__init__(msg)
        self.result = result


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
    group.addoption('--ansible-connection',
                    action='store',
                    dest='ansible_connection',
                    default=ansible.constants.DEFAULT_TRANSPORT,
                    help="connection type to use (default: %default)")
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

    def __init__(self, **kwargs):
        self.module_name = None
        self.options = kwargs
        self.inventory = None
        self.pattern = None

        assert 'inventory' in self.options, "Missing required keyword argument 'inventory'"
        self.inventory = self.options.get('inventory')
        assert 'host_pattern' in self.options, "Missing required keyword argument 'host_pattern'"
        self.pattern = self.options.get('host_pattern')

        # Initialize ansible inventory manage
        self.inventory_manager = ansible.inventory.Inventory(self.inventory)

    def __getattr__(self, name):
        self.module_name = name
        log.debug("__getattr__(%s)" % name)
        log.debug("dict: %s" % self.__dict__)
        if name in self.__dict__:
            log.debug("__getattr__(%s) returning builtin" % name)
            return self.__dict__[name]

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

        # Assemble module argument string
        module_args = list()
        if args:
            module_args += list(args)
        module_args = ' '.join(module_args)

        # Assert hosts matching the provided pattern exist
        hosts = self.inventory_manager.list_hosts(self.pattern)
        if len(hosts) == 0:
            raise AnsibleNoHostsMatch("No hosts match:'%s'" % self.pattern)

        # Log the module and parameters
        log.debug("[%s] %s: %s, %s" % (self.pattern, self.module_name, module_args, kwargs))

        # Build module runner object
        runner = ansible.runner.Runner(
            inventory=self.inventory_manager,
            pattern=self.pattern,
            module_name=self.module_name,
            transport=self.options.get('connection'),
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
            raise AnsibleHostUnreachable("Host unreachable", results)

        # No hosts contacted
        # if not results['contacted']:
        #     raise ansible.errors.AnsibleConnectionFailed("Provided hosts list is empty")

        # Success!
        return results
        # return results['contacted']
        # return results['contacted'][self.pattern]


@pytest.fixture(scope='function')
def ansible_module(request):
    '''
    Return initialized ansibleWrapper
    '''

    # Grab options from command-line
    kwargs = dict()
    kwfields = ('ansible_inventory', 'ansible_host_pattern',
                'ansible_connection', 'ansible_user', 'ansible_sudo', 'ansible_sudo_user')
    for key in kwfields:
        short_key = key[8:]
        kwargs[short_key] = request.config.getvalue(key)

    # Override options from @pytest.mark.ansible
    ansible_args = getattr(request.function, 'ansible', None)
    if ansible_args:
        for key in kwfields:
            short_key = key[8:]
            if short_key not in ansible_args.kwargs:
                continue
            kwargs[short_key] = ansible_args.kwargs[short_key]
            log.debug("Override %s:%s" % (short_key, kwargs[short_key]))

    return AnsibleModule(**kwargs)


@pytest.fixture(scope='function')
def ansible_facts(ansible_module):
    '''
    Return ansible_facts dictionary
    '''
    try:
        return ansible_module.setup()
    except AnsibleHostUnreachable, e:
        return e.result
