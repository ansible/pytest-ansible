"""Define BaseModuleDispatcher class."""

from pytest_ansible.errors import AnsibleModuleError


class BaseModuleDispatcher(object):

    """Fixme.."""

    required_kwargs = ('inventory',)

    def __init__(self, **kwargs):
        """Save provided keyword arguments and assert required values have been provided."""
        self.options = kwargs

        # Assert the expected kwargs were provided
        self.check_required_kwargs(**kwargs)

    def __len__(self):
        """Return the number of hosts that match the `host_pattern`."""
        return len(self.options['inventory_manager'].list_hosts(self.options['host_pattern']))

    def __contains__(self, item):
        """Return the whether the inventory contains a host matching the provided `item`."""
        return len(self.options['inventory_manager'].list_hosts(item)) > 0

    def __getattr__(self, name):
        """Run the ansible module matching the provided `name`.

        Raise `AnsibleModuleError` when no such module exists.
        """
        if not self.has_module(name):
            # TODO: should we just raise an AttributeError, or a more
            # raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__.__name__, name))
            raise AnsibleModuleError("The module {0} was not found in configured module paths.".format(name))
        else:
            self.options['module_name'] = name
            return self._run

    def check_required_kwargs(self, **kwargs):
        """Raise a TypeError if any required kwargs are missing."""
        for kwarg in self.required_kwargs:
            if kwarg not in self.options:
                raise TypeError("Missing required keyword argument '%s'" % kwarg)

    def has_module(self, name):
        """Return whether ansible provides the requested module."""
        raise RuntimeError("Must be implemented by a sub-class")

    def _run(self, *args, **kwargs):
        """Raise a runtime error, unless implemented by sub-classes."""
        raise RuntimeError("Must be implemented by a sub-class")
