from unittest import mock

from pytest_ansible.plugin import PyTestAnsiblePlugin


class MockItem:
    """Mock class for item object"""

    def __init__(self, fixturenames, marker=None):
        self.fixturenames = fixturenames
        self.marker = marker

    def get_closest_marker(self, marker_name):
        return self.marker


class MockConfig:
    """Mock class for config object"""

    options = {}

    def setoption(self, option_name, value):
        self.options[option_name] = value

    def getoption(self, option_name):
        return self.options.get(option_name)


def test_pytest_collection_modifyitems_with_marker():
    # Mock configuration with ansible_ marker
    mock_config = MockConfig()
    mock_config.setoption("ansible_host_pattern", "some_pattern")
    mock_config.setoption("ansible_inventory", "some_inventory")

    plugin = PyTestAnsiblePlugin(mock_config)
    items = [
        MockItem(
            fixturenames=["ansible_fixture"],
            marker=mock.Mock(name="ansible_marker"),
        ),
    ]

    # With the marker, ensure that assert_required_ansible_parameters is not called
    with mock.patch.object(plugin, "assert_required_ansible_parameters"):
        plugin.pytest_collection_modifyitems(None, mock_config, items)


def test_pytest_collection_modifyitems_without_marker():
    # Mock configuration without ansible_ marker
    mock_config = MockConfig()
    mock_config.setoption("ansible_host_pattern", "some_pattern")
    mock_config.setoption("ansible_inventory", "some_inventory")

    plugin = PyTestAnsiblePlugin(mock_config)
    items = [MockItem(fixturenames=["ansible_fixture"])]

    # Without the marker, ensure that assert_required_ansible_parameters is called
    with mock.patch.object(plugin, "assert_required_ansible_parameters") as mock_assert:
        plugin.pytest_collection_modifyitems(None, mock_config, items)
        mock_assert.assert_called_once()


def test_pytest_collection_modifyitems_no_fixtures():
    # Mock configuration without ansible_ marker
    mock_config = MockConfig()
    mock_config.setoption("ansible_host_pattern", "some_pattern")
    mock_config.setoption("ansible_inventory", "some_inventory")

    plugin = PyTestAnsiblePlugin(mock_config)
    items = [MockItem(fixturenames=[])]

    # With no fixtures, ensure that assert_required_ansible_parameters is not called
    with mock.patch.object(plugin, "assert_required_ansible_parameters") as mock_assert:
        plugin.pytest_collection_modifyitems(None, mock_config, items)
        mock_assert.assert_not_called()
