"""Fixme."""

import ansible


class BaseHostManager:
    """The BaseHostManager class provides a base class for managing ansible inventory hosts.

    It's getitem method invokes the module dispatcher with a plugin name.

    Attributes:
        _required_kwargs: A tuple of required keyword arguments.

    """

    _required_kwargs = ("inventory",)

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN002, ANN003, ARG002
        """Fixme."""
        self.options = kwargs

        self.check_required_kwargs(**kwargs)  # type: ignore[no-untyped-call]

        # Sub-classes should override this value
        self._dispatcher = self._default_dispatcher

        # Initialize ansible inventory manager
        self.initialize_inventory()  # type: ignore[no-untyped-call]

    def _default_dispatcher(self, **kwargs):  # type: ignore[no-untyped-def]  # noqa: ANN003, ANN202
        pass

    def get_extra_inventory_hosts(self, host_pattern=None):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
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

    def get_extra_inventory_groups(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Fixme."""
        try:
            extra_inventory_groups = self.options["extra_inventory_manager"].groups
        except KeyError:
            extra_inventory_groups = []
        return extra_inventory_groups

    def check_required_kwargs(self, **kwargs):  # type: ignore[no-untyped-def]  # noqa: ANN003, ANN201, ARG002
        """Raise a TypeError if any required kwargs are missing."""
        for kwarg in self._required_kwargs:
            if kwarg not in self.options:
                msg = f"Missing required keyword argument '{kwarg}'"
                raise TypeError(msg)

    def has_matching_inventory(self, host_pattern):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
        """Return whether any matching ansible inventory is found for the provided host_pattern."""
        try:
            return (
                len(self.options["inventory_manager"].list_hosts(host_pattern)) > 0
                or host_pattern in self.options["inventory_manager"].groups
                or len(self.get_extra_inventory_hosts(host_pattern)) > 0  # type: ignore[no-untyped-call]
                or host_pattern in self.get_extra_inventory_groups()  # type: ignore[no-untyped-call]
            )
        except ansible.errors.AnsibleError:
            return False

    def __getitem__(self, item):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN204
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
        if not self.has_matching_inventory(item):  # type: ignore[no-untyped-call]
            raise KeyError(item)
        self.options["host_pattern"] = item
        return self._dispatcher(**self.options)  # type: ignore[no-untyped-call]

    def __getattr__(self, attr):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN204
        """Return a ModuleDispatcher instance described the provided `attr`."""
        if not self.has_matching_inventory(attr):  # type: ignore[no-untyped-call]
            msg = f"type HostManager has no attribute '{attr}'"
            raise AttributeError(msg)
        self.options["host_pattern"] = attr
        return self._dispatcher(**self.options)  # type: ignore[no-untyped-call]

    def keys(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Fixme."""
        inventory_hosts = [h.name for h in self.options["inventory_manager"].list_hosts()]
        extra_inventory_hosts = self.get_extra_inventory_hosts()  # type: ignore[no-untyped-call]
        return inventory_hosts + extra_inventory_hosts

    def __iter__(self):  # type: ignore[no-untyped-def]  # noqa: ANN204
        """Return an iterator for hosts matching the `host_pattern`."""
        extra_hosts = self.get_extra_inventory_hosts(  # type: ignore[no-untyped-call]
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
            self.get_extra_inventory_hosts(),  # type: ignore[no-untyped-call]
        )

    def __contains__(self, item) -> bool:  # type: ignore[no-untyped-def]  # noqa: ANN001
        """Return whether there is inventory matching the provided `item`."""
        return self.has_matching_inventory(item)  # type: ignore[no-any-return, no-untyped-call]

    def initialize_inventory(self):  # type: ignore[no-untyped-def]  # noqa: ANN201
        """Fixme."""
        msg = "Must be implemented by sub-class"
        raise NotImplementedError(msg)
