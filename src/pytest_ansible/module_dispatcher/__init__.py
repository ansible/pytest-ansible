"""Define BaseModuleDispatcher class."""

from collections.abc import Sequence

from pytest_ansible.errors import AnsibleModuleError


class BaseModuleDispatcher:
    """Fixme.."""

    required_kwargs: Sequence[str] = ("inventory",)

    def __init__(self, **kwargs) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN003, ANN101
        """Save provided keyword arguments and assert required values have been provided."""
        self.options = kwargs

        # Assert the expected kwargs were provided
        self.check_required_kwargs(**kwargs)  # type: ignore[no-untyped-call]

    def __len__(self) -> int:  # noqa: ANN101
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

    def __contains__(self, item) -> bool:  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN101
        """Return the whether the inventory or extra_inventory contains a host matching the provided `item`."""  # noqa: E501
        try:
            extra_inventory_hosts = self.options["extra_inventory_manager"].list_hosts(
                item,
            )
        except KeyError:
            extra_inventory_hosts = []
        return (
            len(self.options["inventory_manager"].list_hosts(item)) + len(extra_inventory_hosts)
        ) > 0

    def __getattr__(self, name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN101, ANN204
        """Run the ansible module matching the provided `name`.

        Raise `AnsibleModuleError` when no such module exists.
        """
        if not self.has_module(name):  # type: ignore[no-untyped-call]
            msg = f"The module {name} was not found in configured module paths."
            raise AnsibleModuleError(
                msg,
            )
        self.options["module_name"] = name
        return self._run

    def check_required_kwargs(self, **kwargs):  # type: ignore[no-untyped-def]  # noqa: ANN003, ANN101, ANN201, ARG002
        """Raise a TypeError if any required kwargs are missing."""
        for kwarg in self.required_kwargs:
            if kwarg not in self.options:
                msg = f"Missing required keyword argument '{kwarg}'"
                raise TypeError(msg)

    def has_module(self, name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN101, ANN201, ARG002
        """Return whether ansible provides the requested module."""
        msg = "Must be implemented by a sub-class"
        raise RuntimeError(msg)

    def _run(self, *args, **kwargs):  # type: ignore[no-untyped-def]  # noqa: ANN002, ANN003, ANN101, ANN202, ARG002
        """Raise a runtime error, unless implemented by sub-classes."""
        msg = "Must be implemented by a sub-class"
        raise RuntimeError(msg)
