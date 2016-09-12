"""Define BaseModuleDispatcher class."""

from pytest_ansible.errors import AnsibleModuleError


class BaseModuleDispatcher(object):

    """Fixme.."""

    required_kwargs = ('inventory',)

    def __init__(self, **kwargs):
        self.options = kwargs

        # Assert the expected kwargs were provided
        self.has_required_kwargs(**kwargs)

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

    def has_required_kwargs(self, **kwargs):
        """Return whether whether the required kwargs were provided during instantiation."""
        for kwarg in self.required_kwargs:
            assert kwarg in self.options, "Missing required keyword argument '%s'" % kwarg
            # The following is a bit of magic and should go away
            # setattr(self, kwarg, kwargs.get(kwarg))

    def has_module(self, name):
        """Return whether ansible provides the requested module."""
        raise RuntimeError("Must be implemented by a sub-class")

    def _run(self, *args, **kwargs):
        """The API provided by ansible is not intended as a public API."""
        raise RuntimeError("Must be implemented by a sub-class")
