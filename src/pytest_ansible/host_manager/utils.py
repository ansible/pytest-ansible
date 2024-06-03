"""Host manager related utilities."""

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pytest_ansible.host_manager import HostManager

from pytest_ansible.has_version import has_ansible_v212, has_ansible_v213


def get_host_manager(*args, **kwargs) -> "HostManager":
    """Initialize and return a HostManager instance.

    Args:
        *args: Positional arguments to pass to the HostManager constructor.
        **kwargs: Keyword arguments to pass to the HostManager constructor.

    Returns:
        HostManager: A HostManager instance.
    """
    if has_ansible_v213:
        from pytest_ansible.host_manager.v213 import HostManagerV213 as HostManager
    elif has_ansible_v212:
        from pytest_ansible.host_manager.v212 import HostManagerV212 as HostManager
    else:
        err = "Unable to find any supported HostManager"
        raise RuntimeError(err)

    return HostManager(*args, **kwargs)
