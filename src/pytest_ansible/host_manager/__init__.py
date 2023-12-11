"""Fixme."""

import ansible

from pytest_ansible.has_version import (
    has_ansible_v212,
    has_ansible_v213,
)


class BaseHostManager:
    """Fixme."""

    _required_kwargs = ("inventory",)

    def __init__(self, *args, **kwargs) -> None:
        """Fixme."""
        self.options = kwargs

        self.check_required_kwargs(**kwargs)

        # Sub-classes should override this value
        self._dispatcher = self._default_dispatcher

        # Initialize ansible inventory manager
        self.initialize_inventory()

    def _default_dispatcher(self, **kwargs):
        pass

    def get_extra_inventory_hosts(self, host_pattern=None):
        """Fixme."""
        try:
            if host_pattern is None:
                extra_inventory_hosts = [
                    h.name for h in self.options["extra_inventory_manager"].list_hosts()
                ]
            else:
                extra_inventory_hosts = [
                    h.name
                    for h in self.options["extra_inventory_manager"].list_hosts(
                        host_pattern,
                    )
                ]
        except KeyError:
            extra_inventory_hosts = []
        return extra_inventory_hosts

    def get_extra_inventory_groups(self):
        """Fixme."""
        try:
            extra_inventory_groups = self.options["extra_inventory_manager"].groups
        except KeyError:
            extra_inventory_groups = []
        return extra_inventory_groups

    def check_required_kwargs(self, **kwargs):
        """Raise a TypeError if any required kwargs are missing."""
        for kwarg in self._required_kwargs:
            if kwarg not in self.options:
                msg = f"Missing required keyword argument '{kwarg}'"
                raise TypeError(msg)

    def has_matching_inventory(self, host_pattern):
        """Return whether any matching ansible inventory is found for the provided host_pattern."""
        try:
            return (
                len(self.options["inventory_manager"].list_hosts(host_pattern)) > 0
                or host_pattern in self.options["inventory_manager"].groups
                or len(self.get_extra_inventory_hosts(host_pattern)) > 0
                or host_pattern in self.get_extra_inventory_groups()
            )
        except ansible.errors.AnsibleError:
            return False

    def __getitem__(self, item):
        """Return a ModuleDispatcher instance described the provided `item`."""
        # Handle slicing
        if isinstance(item, slice):
            new_item = "all["
            if item.start is not None:
                new_item += str(item.start)
            new_item += "-"
            if item.stop is not None:
                new_item += str(item.stop)
            item = new_item + "]"

        if item in self.__dict__:
            return self.__dict__[item]
        if not self.has_matching_inventory(item):
            raise KeyError(item)
        self.options["host_pattern"] = item
        return self._dispatcher(**self.options)

    def __getattr__(self, attr):
        """Return a ModuleDispatcher instance described the provided `attr`."""
        if not self.has_matching_inventory(attr):
            msg = f"type HostManager has no attribute '{attr}'"
            raise AttributeError(msg)
        self.options["host_pattern"] = attr
        return self._dispatcher(**self.options)

    def keys(self):
        """Fixme."""
        inventory_hosts = [
            h.name for h in self.options["inventory_manager"].list_hosts()
        ]
        extra_inventory_hosts = self.get_extra_inventory_hosts()
        return inventory_hosts + extra_inventory_hosts

    def __iter__(self):
        """Return an iterator for hosts matching the `host_pattern`."""
        extra_hosts = self.get_extra_inventory_hosts(
            host_pattern=self.options["host_pattern"],
        )
        all_hosts = self.options["inventory_manager"].list_hosts(
            self.options["host_pattern"],
        )
        # Return only the name (ala .keys()
        # Return a BaseHostManager instance initialized for each host in the inventory
        # Return a ModuleDispatcher representing the group
        return iter([self[h] for h in all_hosts + extra_hosts])

    def __len__(self) -> int:
        """Return the number of inventory hosts."""
        return len(self.options["inventory_manager"].list_hosts()) + len(
            self.get_extra_inventory_hosts(),
        )

    def __contains__(self, item) -> bool:
        """Return whether there is inventory matching the provided `item`."""
        return self.has_matching_inventory(item)

    def initialize_inventory(self):
        """Fixme."""
        msg = "Must be implemented by sub-class"
        raise NotImplementedError(msg)


def get_host_manager(*args, **kwargs):
    """Initialize and return a HostManager instance."""
    if has_ansible_v213:
        from pytest_ansible.host_manager.v213 import HostManagerV213 as HostManager
    elif has_ansible_v212:
        from pytest_ansible.host_manager.v212 import HostManagerV212 as HostManager
    else:
        raise RuntimeError("Unable to find any supported HostManager")

    return HostManager(*args, **kwargs)
