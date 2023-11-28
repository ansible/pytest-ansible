"""Define BaseModuleDispatcher class."""

from collections.abc import Sequence

from pytest_ansible.errors import AnsibleModuleError


class BaseModuleDispatcher:
    """Fixme.."""

    required_kwargs: Sequence[str] = ("inventory",)

    def __init__(self, **kwargs) -> None:
        """Save provided keyword arguments and assert required values have been provided."""
        self.options = kwargs

        # Assert the expected kwargs were provided
        self.check_required_kwargs(**kwargs)

    def __len__(self) -> int:
        """Return the number of hosts that match the `host_pattern`."""
        try:
            extra_inventory_hosts = self.options["extra_inventory_manager"].list_hosts(
                self.options["host_pattern"],
            )
        except KeyError:
            extra_inventory_hosts = []
        return len(
            self.options["inventory_manager"].list_hosts(self.options["host_pattern"]),
        ) + len(extra_inventory_hosts)

    def __contains__(self, item) -> bool:
        """Return the whether the inventory or extra_inventory contains a host matching the provided `item`."""
        try:
            extra_inventory_hosts = self.options["extra_inventory_manager"].list_hosts(
                item,
            )
        except KeyError:
            extra_inventory_hosts = []
        return (
            len(self.options["inventory_manager"].list_hosts(item))
            + len(extra_inventory_hosts)
        ) > 0

    def __getattr__(self, name):
        """Run the ansible module matching the provided `name`.

        Raise `AnsibleModuleError` when no such module exists.
        """
        if not self.has_module(name):
            msg = f"The module {name} was not found in configured module paths."
            raise AnsibleModuleError(
                msg,
            )
        self.options["module_name"] = name
        return self._run

    def check_required_kwargs(self, **kwargs):
        """Raise a TypeError if any required kwargs are missing."""
        for kwarg in self.required_kwargs:
            if kwarg not in self.options:
                msg = f"Missing required keyword argument '{kwarg}'"
                raise TypeError(msg)

    def has_module(self, name):
        """Return whether ansible provides the requested module."""
        msg = "Must be implemented by a sub-class"
        raise RuntimeError(msg)

    def _run(self, *args, **kwargs):
        """Raise a runtime error, unless implemented by sub-classes."""
        msg = "Must be implemented by a sub-class"
        raise RuntimeError(msg)
