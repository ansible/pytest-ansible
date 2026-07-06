"""Test the plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock
from unittest.mock import MagicMock

from pytest_ansible.plugin import PyTestAnsiblePlugin, pytest_generate_tests

from .conftest import skip_ansible_219


if TYPE_CHECKING:
    import pytest


class MockItem:
    """Mock class for item object."""

    def __init__(self, fixturenames, marker=None) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001, D107
        self.fixturenames = fixturenames
        self.marker = marker

    def get_closest_marker(self, marker_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG002, D102
        return self.marker


class MockConfig:
    """Mock class for config object.

    Attributes:
        options: A dictionary of options.
    """

    options = {}  # type: ignore[var-annotated]  # noqa: RUF012

    def setoption(self, option_name, value):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D102
        self.options[option_name] = value

    def getoption(self, option_name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D102
        return self.options.get(option_name)

    def __init__(self) -> None:  # noqa: D107
        self.options = {
            "ansible_host_pattern": "localhost",
            "ansible_inventory": "/etc/ansible/hosts",
        }


class MockPluginManager:
    """Mock class for pluginmanager object."""

    def getplugin(self, name):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG002, D102
        return MagicMock()


class MockMetafunc:
    """Mock class for metafunc object."""

    def __init__(self, fixturenames) -> None:  # type: ignore[no-untyped-def]  # noqa: ANN001, D107
        self.fixturenames = fixturenames
        self.config = MockConfig()
        self.parametrize = MagicMock()


@skip_ansible_219
def test_pytest_generate_tests_with_ansible_host():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    metafunc = MagicMock()
    metafunc.fixturenames = ["ansible_host"]
    metafunc.config = MagicMock()

    # Mock config values
    metafunc.config.getoption.side_effect = {
        "ansible_host_pattern": "localhost",
        "ansible_inventory": "/etc/ansible/hosts",
    }.get

    plugin = PyTestAnsiblePlugin(metafunc.config)

    # Mock Ansible host initialization
    host = MagicMock()
    host.name = "localhost"
    plugin.initialize = MagicMock(return_value={"localhost": host})  # type: ignore[method-assign]

    pytest_generate_tests(metafunc)  # type: ignore[no-untyped-call]

    assert metafunc.parametrize.call_count == 1


@skip_ansible_219
def test_pytest_generate_tests_with_ansible_group():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    metafunc = MagicMock()
    metafunc.fixturenames = ["ansible_group"]
    config = MagicMock()
    config.pluginmanager = MagicMock()
    metafunc.config = config

    plugin = PyTestAnsiblePlugin(metafunc.config)

    # Mock Ansible host initialization
    host1 = MagicMock()
    host1.name = "host1"
    group1 = MagicMock()
    group1.name = "group1"
    host1.groups = [group1]

    host2 = MagicMock()
    host2.name = "host2"
    group2 = MagicMock()
    group2.name = "group2"
    host2.groups = [group2]

    plugin.initialize = MagicMock(return_value={"host1": host1, "host2": host2})  # type: ignore[method-assign]

    pytest_generate_tests(metafunc)  # type: ignore[no-untyped-call]

    assert metafunc.parametrize.call_count == 2  # noqa: PLR2004  # Called twice for ansible_group


def test_pytest_collection_modifyitems_with_marker():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    # Mock configuration with ansible_ marker
    mock_config = MockConfig()
    mock_config.setoption("ansible_host_pattern", "some_pattern")  # type: ignore[no-untyped-call]
    mock_config.setoption("ansible_inventory", "some_inventory")  # type: ignore[no-untyped-call]

    plugin = PyTestAnsiblePlugin(mock_config)
    items = [
        MockItem(
            fixturenames=["ansible_fixture"],
            marker=mock.Mock(name="ansible_marker"),
        ),
    ]

    # With the marker, ensure that assert_required_ansible_parameters is not called
    with mock.patch.object(plugin, "assert_required_ansible_parameters"):
        plugin.pytest_collection_modifyitems(mock_config, items)  # type: ignore[no-untyped-call]


def test_pytest_collection_modifyitems_without_marker():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    # Mock configuration without ansible_ marker
    mock_config = MockConfig()
    mock_config.setoption("ansible_host_pattern", "some_pattern")  # type: ignore[no-untyped-call]
    mock_config.setoption("ansible_inventory", "some_inventory")  # type: ignore[no-untyped-call]

    plugin = PyTestAnsiblePlugin(mock_config)
    items = [MockItem(fixturenames=["ansible_adhoc"])]

    # Without the marker, ensure that assert_required_ansible_parameters is called
    with mock.patch.object(plugin, "assert_required_ansible_parameters") as mock_assert:
        plugin.pytest_collection_modifyitems(mock_config, items)  # type: ignore[no-untyped-call]
        mock_assert.assert_called_once()


def test_pytest_collection_modifyitems_no_fixtures():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    # Mock configuration without ansible_ marker
    mock_config = MockConfig()
    mock_config.setoption("ansible_host_pattern", "some_pattern")  # type: ignore[no-untyped-call]
    mock_config.setoption("ansible_inventory", "some_inventory")  # type: ignore[no-untyped-call]

    plugin = PyTestAnsiblePlugin(mock_config)
    items = [MockItem(fixturenames=[])]

    # With no fixtures, ensure that assert_required_ansible_parameters is not called
    with mock.patch.object(plugin, "assert_required_ansible_parameters") as mock_assert:
        plugin.pytest_collection_modifyitems(mock_config, items)  # type: ignore[no-untyped-call]
        mock_assert.assert_not_called()


def test_any_item_uses_ansible_fixtures_skips_items_without_fixturenames():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Items without a fixturenames attribute are silently skipped."""

    class NoFixtureItem:
        pass

    result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(
        [NoFixtureItem()],
    )
    assert result is False


def test_any_item_uses_ansible_fixtures_skips_request_fixture():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """The reserved 'request' fixture name should be silently skipped."""
    result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(
        [MockItem(fixturenames=["request"])],
    )
    assert result is False


def test_any_item_uses_ansible_fixtures_skips_known_fixture_defs():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Fixtures present in _fixtureinfo.name2fixturedefs are skipped."""

    class ItemWithFixtureDefs:
        fixturenames = ["my_custom_fixture"]  # noqa: RUF012

        class _fixtureinfo:  # noqa: N801
            name2fixturedefs = {"my_custom_fixture": [MagicMock()]}  # noqa: RUF012

    result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(
        [ItemWithFixtureDefs()],
    )
    assert result is False


def test_any_item_uses_ansible_fixtures_returns_true_for_ansible_fixture():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Return True when an item uses an OUR_FIXTURES fixture."""
    result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(
        [MockItem(fixturenames=["ansible_adhoc"])],
    )
    assert result is True


def test_any_item_uses_ansible_fixtures_logs_undefined(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Fixtures with no definition and not 'request' trigger a log error.

    Args:
        caplog: pytest log capture fixture
    """
    import logging

    with caplog.at_level(logging.ERROR, logger="pytest_ansible.plugin"):
        result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(
            [MockItem(fixturenames=["unknown_fixture"])],
        )
    assert result is False
    assert "unknown_fixture" in caplog.text


def test_any_item_uses_ansible_fixtures_fixtureinfo_miss():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Fixture present in _fixtureinfo but not matching name2fixturedefs falls through."""

    class ItemWithPartialFixtureDefs:
        """Item where fixture is NOT in name2fixturedefs."""

        fixturenames = ["other_fixture"]  # noqa: RUF012

        class _fixtureinfo:  # noqa: N801
            name2fixturedefs = {"different_fixture": [MagicMock()]}  # noqa: RUF012

    result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(
        [ItemWithPartialFixtureDefs()],
    )
    assert result is False


def test_any_item_uses_ansible_fixtures_no_name2fixturedefs():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Item with _fixtureinfo but without name2fixturedefs attribute."""

    class ItemWithBareFixtureInfo:
        """Item where _fixtureinfo lacks name2fixturedefs."""

        fixturenames = ["some_fixture"]  # noqa: RUF012

        class _fixtureinfo:  # noqa: N801
            pass

    result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(
        [ItemWithBareFixtureInfo()],
    )
    assert result is False


def test_pytest_collect_file_no_molecule_option():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Return None when config.option has no molecule attribute."""
    from pytest_ansible.plugin import pytest_collect_file

    parent = MagicMock()
    del parent.config.option.molecule

    result = pytest_collect_file(file_path=None, parent=parent)
    assert result is None


def test_pytest_collect_file_molecule_disabled():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Return None when --molecule is not enabled."""
    from pytest_ansible.plugin import pytest_collect_file

    parent = MagicMock()
    parent.config.option.molecule = False

    result = pytest_collect_file(file_path=None, parent=parent)
    assert result is None


def test_pytest_collect_file_symlink(tmp_path):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Return None for symlinked files.

    Args:
        tmp_path: pytest tmp_path fixture
    """
    from pytest_ansible.plugin import pytest_collect_file

    real_file = tmp_path / "real_molecule.yml"
    real_file.write_text("---\n")
    symlink = tmp_path / "molecule.yml"
    symlink.symlink_to(real_file)

    parent = MagicMock()
    parent.config.option.molecule = True

    result = pytest_collect_file(file_path=symlink, parent=parent)
    assert result is None


def test_pytest_collect_file_non_molecule_yml(tmp_path):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Return None for files not named molecule.yml.

    Args:
        tmp_path: pytest tmp_path fixture
    """
    from pytest_ansible.plugin import pytest_collect_file

    other_file = tmp_path / "playbook.yml"
    other_file.write_text("---\n")

    parent = MagicMock()
    parent.config.option.molecule = True

    result = pytest_collect_file(file_path=other_file, parent=parent)
    assert result is None


def test_warn_or_fail_on_v219():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """On Ansible 2.19+, warn_or_fail should call pytest.exit."""
    from unittest.mock import patch

    from pytest_ansible.plugin import warn_or_fail

    with (
        patch("pytest_ansible.plugin.has_ansible_v219", True),  # noqa: FBT003
        patch("pytest_ansible.plugin.pytest") as mock_pytest,
    ):
        warn_or_fail("ansible_host")
        mock_pytest.exit.assert_called_once()


def test_warn_or_fail_pre_v219():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Before Ansible 2.19, warn_or_fail should emit a DeprecationWarning."""
    import warnings

    from unittest.mock import patch

    from pytest_ansible.plugin import warn_or_fail

    with (
        patch("pytest_ansible.plugin.has_ansible_v219", False),  # noqa: FBT003
        warnings.catch_warnings(record=True) as caught,
    ):
        warnings.simplefilter("always")
        warn_or_fail("ansible_host")

    assert len(caught) == 1
    assert issubclass(caught[0].category, DeprecationWarning)
    assert "ansible_host" in str(caught[0].message)
