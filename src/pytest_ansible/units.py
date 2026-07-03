"""Setup the collection for testing."""

from __future__ import annotations

import logging
import os
import sys

from pathlib import Path


logger = logging.getLogger(__name__)

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    HAS_ANSIBLE = True
except ImportError:
    HAS_ANSIBLE = False

try:
    from ansible.utils.collection_loader._collection_finder import (
        _AnsibleCollectionFinder,
    )

    HAS_COLLECTION_FINDER = True
except ImportError:
    HAS_COLLECTION_FINDER = False


def get_collection_name(start_path: Path) -> tuple[str | None, str | None]:
    """Get the collection namespace and name from the galaxy.yml file.

    Args:
        start_path: The path to the root of the collection

    Returns:
        A tuple of the namespace and name
    """
    info_file = start_path / "galaxy.yml"
    logger.info("Looking for collection info in %s", info_file)

    try:
        with info_file.open(encoding="utf-8") as file_handler:
            galaxy_info = yaml.safe_load(file_handler)
    except FileNotFoundError:
        logger.error("No galaxy.yml file found, plugin not activated")  # noqa: TRY400
        return None, None

    try:
        namespace = galaxy_info["namespace"]
        name = galaxy_info["name"]
    except KeyError:
        logger.error("galaxy.yml file does not contain namespace and name")  # noqa: TRY400
        return None, None

    logger.debug("galaxy.yml file found, plugin activated")
    logger.info("Collection namespace: %s", namespace)
    logger.info("Collection name: %s", name)
    return namespace, name


def _resolve_collections_dir(
    start_path: Path,
    namespace: str,
    name: str,
) -> Path:
    """Return the collections root directory, creating symlinks when needed.

    :param start_path: The path where pytest was invoked.
    :param namespace: The collection namespace.
    :param name: The collection name.
    :returns: Path to the directory containing ``ansible_collections/``.
    """
    collection_tree = ("collections", "ansible_collections", namespace, name)
    if start_path.parts[-4:] == collection_tree:
        logger.info("In collection tree")
        return start_path.parents[2]

    logger.info("Not in collection tree")
    collections_dir = start_path / "collections"
    name_dir = collections_dir / "ansible_collections" / namespace / name

    if not name_dir.is_dir():
        name_dir.mkdir(parents=True, exist_ok=True)
        for entry in start_path.iterdir():
            if entry.name == "collections":
                continue
            Path(name_dir / entry.name).symlink_to(entry)

    return collections_dir


def inject(start_path: Path) -> None:
    """Inject the collection path.

    In the case of ansible > 2.9, initialize the collection finder with the collection path
    otherwise, inject the collection path into sys.path.

    :param start_path: The path where pytest was invoked
    """
    if not HAS_ANSIBLE:
        logger.error("ansible is not installed, plugin not activated")
        return
    if not HAS_YAML:
        logger.error("pyyaml is not installed, plugin not activated")
        return

    logger.debug("Start path: %s", start_path)
    namespace, name = get_collection_name(start_path)
    if namespace is None or name is None:
        return

    collections_dir = _resolve_collections_dir(start_path, namespace, name)

    additional_collections_paths: list[str] = [
        Path("~/.ansible/collections").expanduser().as_posix()
    ]

    if "COLLECTIONS_PATH" in os.environ and "COLLECTIONS_PATHS" in os.environ:
        additional_collections_paths.extend(
            os.environ.get("COLLECTIONS_PATH", "").split(os.pathsep)
            + os.environ.get("COLLECTIONS_PATHS", "").split(os.pathsep),
        )
    logger.info("Additional Collections Paths: %s", additional_collections_paths)

    acf_inject(paths=[str(collections_dir), *additional_collections_paths])

    sys.path.insert(0, str(collections_dir))
    logger.debug("sys.path updated: %s", sys.path)

    envvar_name = determine_envvar()
    additional_collections_paths = [str(path) for path in additional_collections_paths]
    env_paths = os.pathsep.join([str(collections_dir), *additional_collections_paths])
    logger.info("Setting %s to %s", envvar_name, env_paths)
    os.environ[envvar_name] = env_paths


def inject_only() -> None:
    """Inject the current ANSIBLE_COLLECTIONS_PATH(S)."""
    envvar_name = determine_envvar()
    env_paths = os.environ.get(envvar_name, "")
    path_list = env_paths.split(os.pathsep)
    for path in path_list:
        if path:
            sys.path.insert(0, path)
    logger.debug("sys.path updated: %s", sys.path)
    acf_inject(paths=path_list)


def acf_inject(paths: list[str]) -> None:
    """Inject the collection path into the AnsibleCollectionFinder.

    :param paths: The paths to inject
    """
    if HAS_COLLECTION_FINDER:
        acf = _AnsibleCollectionFinder(paths=paths)
        acf._install()  # noqa: SLF001
        logger.debug("_ACF installed: %s", paths)
        logger.debug("_ACF configured paths: %s", acf._n_configured_paths)  # noqa: SLF001
    else:
        logger.debug("_ACF not available")


def determine_envvar() -> str:
    """Use the existence of the AnsibleCollectionFinder to determine the ansible version.

    Ansible 2.9 did not have AnsibleCollectionFinder and did not support ANSIBLE_COLLECTIONS_PATH later versions do.

    Returns:
        The appropriate environment variable to use
    """  # noqa: E501
    if not HAS_COLLECTION_FINDER:
        return "ANSIBLE_COLLECTIONS_PATHS"
    return "ANSIBLE_COLLECTIONS_PATH"
