"""Host manager related utilities."""

from pytest_ansible.has_version import has_ansible_v213
from pytest_ansible.host_manager.base import BaseHostManager


def get_host_manager(*args, **kwargs) -> BaseHostManager:  # type: ignore[no-untyped-def]  # noqa: ANN002, ANN003
    """Initialize and return a HostManager instance.

    Args:
        *args: Positional arguments to pass to the HostManager constructor.
        **kwargs: Keyword arguments to pass to the HostManager constructor.

    Returns:
        HostManager: A HostManager instance.
    """
    if has_ansible_v213:
        from pytest_ansible.host_manager.v213 import HostManagerV213 as HostManager
    else:
        err = "Unable to find any supported HostManager"
        raise RuntimeError(err)

    return HostManager(*args, **kwargs)
