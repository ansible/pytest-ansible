"""Test the plugin."""

from __future__ import annotations

from unittest import mock
from unittest.mock import MagicMock

from pytest_ansible.plugin import PyTestAnsiblePlugin, pytest_generate_tests

from .conftest import skip_ansible_219


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


def test_any_item_uses_ansible_fixtures_skips_items_without_fixturenames():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    """Items without a fixturenames attribute are silently skipped."""

    class NoFixtureItem:  # noqa: D101
        pass

    result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(  # type: ignore[no-untyped-call]
        [NoFixtureItem()],
    )
    assert result is False


def test_any_item_uses_ansible_fixtures_skips_request_fixture():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    """The reserved 'request' fixture name should be silently skipped."""
    result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(  # type: ignore[no-untyped-call]
        [MockItem(fixturenames=["request"])],
    )
    assert result is False


def test_any_item_uses_ansible_fixtures_skips_known_fixture_defs():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    """Fixtures present in _fixtureinfo.name2fixturedefs are skipped."""

    class ItemWithFixtureDefs:  # noqa: D101
        fixturenames = ["my_custom_fixture"]

        class _fixtureinfo:  # noqa: N801, D106
            name2fixturedefs = {"my_custom_fixture": [MagicMock()]}

    result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(  # type: ignore[no-untyped-call]
        [ItemWithFixtureDefs()],
    )
    assert result is False


def test_any_item_uses_ansible_fixtures_returns_true_for_ansible_fixture():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    """Return True when an item uses an OUR_FIXTURES fixture."""
    result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(  # type: ignore[no-untyped-call]
        [MockItem(fixturenames=["ansible_adhoc"])],
    )
    assert result is True


def test_any_item_uses_ansible_fixtures_logs_undefined(caplog):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    """Fixtures with no definition and not 'request' trigger a log error."""
    import logging

    with caplog.at_level(logging.ERROR):
        result = PyTestAnsiblePlugin._any_item_uses_ansible_fixtures(  # type: ignore[no-untyped-call]
            [MockItem(fixturenames=["unknown_fixture"])],
        )
    assert result is False
    assert "unknown_fixture" in caplog.text
