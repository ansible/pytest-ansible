"""Test the plugin."""

from __future__ import annotations

import logging

from typing import TYPE_CHECKING
from unittest import mock
from unittest.mock import MagicMock, patch

import ansible.errors
import pytest

from pytest_ansible.plugin import (
    PyTestAnsiblePlugin,
    pytest_addoption,
    pytest_collect_file,
    pytest_configure,
    pytest_generate_tests,
)

from .conftest import skip_ansible_219


if TYPE_CHECKING:
    from pathlib import Path


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

    metafunc.parametrize.assert_called_once()


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
    parent = MagicMock()
    del parent.config.option.molecule

    result = pytest_collect_file(file_path=None, parent=parent)
    assert result is None


def test_pytest_collect_file_molecule_disabled():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Return None when --molecule is not enabled."""
    parent = MagicMock()
    parent.config.option.molecule = False

    result = pytest_collect_file(file_path=None, parent=parent)
    assert result is None


def test_pytest_collect_file_symlink(tmp_path):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201
    """Return None for symlinked files.

    Args:
        tmp_path: pytest tmp_path fixture
    """
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
    other_file = tmp_path / "playbook.yml"
    other_file.write_text("---\n")

    parent = MagicMock()
    parent.config.option.molecule = True

    result = pytest_collect_file(file_path=other_file, parent=parent)
    assert result is None


def test_warn_or_fail_on_v219():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """On Ansible 2.19+, warn_or_fail should call pytest.exit."""
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


def test_pytest_load_initial_conftests_connection_equals():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """The --connection=value form should also trigger a deprecation warning."""
    import warnings

    from pytest_ansible.plugin import pytest_load_initial_conftests

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        pytest_load_initial_conftests(args=["--connection=local"])

    assert len(caught) == 1
    assert issubclass(caught[0].category, DeprecationWarning)
    assert "--ansible-connection" in str(caught[0].message)


def test_pytest_load_initial_conftests_no_connection():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """No warning emitted when --connection is absent."""
    import warnings

    from pytest_ansible.plugin import pytest_load_initial_conftests

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        pytest_load_initial_conftests(args=["--verbose", "--ansible-connection=local"])

    assert len(caught) == 0


def test_pytest_addoption_without_ansible() -> None:
    """pytest_addoption returns early when ansible is not installed."""
    with patch("pytest_ansible.plugin.HAS_ANSIBLE", new=False):
        pytest_addoption(MagicMock())


def test_pytest_configure_without_ansible() -> None:
    """pytest_configure returns early when ansible is not installed."""
    with patch("pytest_ansible.plugin.HAS_ANSIBLE", new=False):
        pytest_configure(MagicMock())


def test_pytest_configure_verbose_and_inject(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """pytest_configure sets verbosity and injects collection path.

    Args:
        tmp_path: Temporary directory for a fake collection root
        monkeypatch: pytest monkeypatch fixture
    """
    (tmp_path / "galaxy.yml").write_text(
        "namespace: ns\nname: col\n",
        encoding="utf-8",
    )
    config = MagicMock()
    config.option.verbose = 2
    config.option.ansible_unit_inject_only = False
    config.invocation_params.dir = tmp_path
    config.pluginmanager.register = MagicMock(return_value=True)
    config.addinivalue_line = MagicMock()
    config.rootpath = tmp_path

    monkeypatch.setattr("pytest_ansible.plugin.inject", MagicMock())
    monkeypatch.setattr("pytest_ansible.plugin._load_scenarios", MagicMock())

    with (
        patch("pytest_ansible.plugin.HAS_ANSIBLE", new=True),
        patch("pytest_ansible.plugin.ansible") as mock_ansible,
    ):
        mock_ansible.utils.VERBOSITY = 0
        pytest_configure(config)
        expected_verbosity = 2
        assert mock_ansible.utils.VERBOSITY == expected_verbosity


def test_pytest_configure_verbose_display_fallback() -> None:
    """pytest_configure uses ansible.utils.display.verbosity when VERBOSITY missing."""
    config = MagicMock()
    config.option.verbose = 1
    config.option.ansible_unit_inject_only = True
    config.pluginmanager.register = MagicMock(return_value=True)
    config.addinivalue_line = MagicMock()
    config.rootpath = MagicMock()

    class Utils:
        display = MagicMock()

    with (
        patch("pytest_ansible.plugin.HAS_ANSIBLE", new=True),
        patch("pytest_ansible.plugin.ansible") as mock_ansible,
        patch("pytest_ansible.plugin.inject_only") as mock_inject_only,
        patch("pytest_ansible.plugin._load_scenarios"),
    ):
        mock_ansible.utils = Utils()
        pytest_configure(config)
        assert mock_ansible.utils.display.verbosity == 1
        mock_inject_only.assert_called_once()


def test_pytest_collect_file_molecule_yml(tmp_path: Path) -> None:
    """pytest_collect_file returns MoleculeFile for molecule.yml.

    Args:
        tmp_path: Temporary directory containing molecule.yml
    """
    mol = tmp_path / "molecule.yml"
    mol.write_text("---\n", encoding="utf-8")
    parent = MagicMock()
    parent.config.option.molecule = True

    with (
        patch("pytest_ansible.plugin.HAS_MOLECULE", new=True),
        patch("pytest_ansible.plugin.warn_molecule_deprecated"),
        patch("pytest_ansible.plugin.MoleculeFile") as mock_file,
    ):
        molecule_node = MagicMock(name="molecule-file")
        mock_file.from_parent.return_value = molecule_node
        result = pytest_collect_file(file_path=mol, parent=parent)

    assert result is molecule_node
    mock_file.from_parent.assert_called_once()


def test_pytest_generate_tests_molecule_scenario_without_molecule() -> None:
    """pytest_generate_tests exits when molecule is missing for molecule_scenario."""
    metafunc = MagicMock()
    metafunc.fixturenames = ["molecule_scenario"]

    with (
        patch("pytest_ansible.plugin.HAS_MOLECULE", new=False),
        patch("pytest_ansible.plugin.warn_molecule_deprecated"),
        patch("pytest_ansible.plugin.pytest") as mock_pytest,
    ):
        pytest_generate_tests(metafunc)  # type: ignore[no-untyped-call]
        mock_pytest.exit.assert_called_once()


def test_pytest_generate_tests_ansible_host_error() -> None:
    """pytest_generate_tests wraps AnsibleError as UsageError for ansible_host."""
    metafunc = MagicMock()
    metafunc.fixturenames = ["ansible_host"]
    metafunc.config.getoption.side_effect = {
        "ansible_host_pattern": "localhost",
        "ansible_inventory": "/etc/ansible/hosts",
    }.get

    plugin = MagicMock()
    plugin.initialize.side_effect = ansible.errors.AnsibleError("fail")
    metafunc.config.pluginmanager.getplugin.return_value = plugin

    with (
        patch("pytest_ansible.plugin.warn_or_fail"),
        patch.object(PyTestAnsiblePlugin, "assert_required_ansible_parameters"),
        pytest.raises(pytest.UsageError),
    ):
        pytest_generate_tests(metafunc)  # type: ignore[no-untyped-call]


def test_pytest_generate_tests_ansible_group_error() -> None:
    """pytest_generate_tests wraps AnsibleError as UsageError for ansible_group."""
    metafunc = MagicMock()
    metafunc.fixturenames = ["ansible_group"]
    metafunc.config.getoption.side_effect = {
        "ansible_host_pattern": "localhost",
        "ansible_inventory": "/etc/ansible/hosts",
    }.get

    plugin = MagicMock()
    plugin.initialize.side_effect = ansible.errors.AnsibleError("fail")
    metafunc.config.pluginmanager.getplugin.return_value = plugin

    with (
        patch("pytest_ansible.plugin.warn_or_fail"),
        patch.object(PyTestAnsiblePlugin, "assert_required_ansible_parameters"),
        pytest.raises(pytest.UsageError),
    ):
        pytest_generate_tests(metafunc)  # type: ignore[no-untyped-call]


def test_pytest_generate_tests_molecule_scenario_parametrizes() -> None:
    """pytest_generate_tests parametrizes molecule_scenario when molecule exists."""
    metafunc = MagicMock()
    metafunc.fixturenames = ["molecule_scenario"]
    scenario = MagicMock()
    scenario.test_id = "role-default"

    with (
        patch("pytest_ansible.plugin.HAS_MOLECULE", new=True),
        patch("pytest_ansible.plugin.warn_molecule_deprecated"),
        patch("pytest_ansible.plugin.scenarios", [scenario]),
    ):
        pytest_generate_tests(metafunc)  # type: ignore[no-untyped-call]

    metafunc.parametrize.assert_called_once_with(
        "molecule_scenario",
        [scenario],
        ids=["role-default"],
    )


def test_plugin_initialize_config_only() -> None:
    """Initialize with only config (no request) covers the request skip branch."""
    config = MagicMock()
    plugin = PyTestAnsiblePlugin(config)
    plugin._load_ansible_config = MagicMock(return_value={"inventory": "inv"})  # type: ignore[method-assign]

    with patch("pytest_ansible.plugin.get_host_manager", return_value="hm") as mock_hm:
        result = plugin.initialize(config=config)  # type: ignore[no-untyped-call]

    assert result == "hm"
    mock_hm.assert_called_once_with(inventory="inv")


def test_plugin_initialize_request_only() -> None:
    """Initialize with only request (no config) covers the config skip branch."""
    request = MagicMock()
    plugin = PyTestAnsiblePlugin(MagicMock())
    plugin._load_request_config = MagicMock(return_value={"user": "u"})  # type: ignore[method-assign]

    with patch("pytest_ansible.plugin.get_host_manager", return_value="hm") as mock_hm:
        result = plugin.initialize(request=request)  # type: ignore[no-untyped-call]

    assert result == "hm"
    mock_hm.assert_called_once_with(user="u")


def test_pytest_generate_tests_ansible_group_mocked() -> None:
    """pytest_generate_tests parametrizes ansible_group from inventory groups."""
    metafunc = MagicMock()
    metafunc.fixturenames = ["ansible_group"]
    metafunc.config.getoption.side_effect = {
        "ansible_host_pattern": "localhost",
        "ansible_inventory": "/etc/ansible/hosts",
    }.get

    hosts = MagicMock()
    hosts.options = {"inventory_manager": MagicMock()}
    hosts.options["inventory_manager"].list_groups.return_value = ["group1"]
    hosts.get_extra_inventory_groups.return_value = ["extra_group"]
    hosts.__getitem__ = MagicMock(side_effect=lambda key: key)

    plugin = MagicMock()
    plugin.initialize.return_value = hosts
    metafunc.config.pluginmanager.getplugin.return_value = plugin

    with (
        patch("pytest_ansible.plugin.warn_or_fail"),
        patch.object(PyTestAnsiblePlugin, "assert_required_ansible_parameters"),
    ):
        pytest_generate_tests(metafunc)  # type: ignore[no-untyped-call]

    metafunc.parametrize.assert_called_once()
    args, _kwargs = metafunc.parametrize.call_args
    assert args[0] == "ansible_group"
    assert list(args[1]) == ["group1", "extra_group"]


def test_pytest_generate_tests_ansible_host_success() -> None:
    """pytest_generate_tests parametrizes ansible_host from inventory hosts."""
    metafunc = MagicMock()
    metafunc.fixturenames = ["ansible_host"]
    metafunc.config.getoption.side_effect = {
        "ansible_host_pattern": "localhost",
        "ansible_inventory": "/etc/ansible/hosts",
    }.get

    hosts = MagicMock()
    hosts.__iter__ = MagicMock(return_value=iter(["localhost"]))
    hosts.__getitem__ = MagicMock(side_effect=lambda key: key)

    plugin = MagicMock()
    plugin.initialize.return_value = hosts
    metafunc.config.pluginmanager.getplugin.return_value = plugin

    with (
        patch("pytest_ansible.plugin.warn_or_fail"),
        patch.object(PyTestAnsiblePlugin, "assert_required_ansible_parameters"),
    ):
        pytest_generate_tests(metafunc)  # type: ignore[no-untyped-call]

    metafunc.parametrize.assert_called_once()


def test_plugin_initialize_merges_config_and_request() -> None:
    """Initialize merges config, request, and kwargs."""
    config = MagicMock()
    request = MagicMock()
    plugin = PyTestAnsiblePlugin(config)

    with patch("pytest_ansible.plugin.get_host_manager", return_value="hm") as mock_hm:
        plugin._load_ansible_config = MagicMock(return_value={"inventory": "inv"})  # type: ignore[method-assign]
        plugin._load_request_config = MagicMock(return_value={"user": "u"})  # type: ignore[method-assign]
        result = plugin.initialize(config=config, request=request, connection="local")  # type: ignore[no-untyped-call]

    assert result == "hm"
    mock_hm.assert_called_once()
    kwargs = mock_hm.call_args.kwargs
    assert kwargs["inventory"] == "inv"
    assert kwargs["user"] == "u"
    assert kwargs["connection"] == "local"


def test_assert_required_ansible_parameters_missing_inventory() -> None:
    """assert_required_ansible_parameters raises when inventory is falsy."""
    config = MagicMock()
    config.getoption.return_value = None
    with pytest.raises(pytest.UsageError, match="Unable to find an inventory file"):
        PyTestAnsiblePlugin.assert_required_ansible_parameters(config)  # type: ignore[no-untyped-call]


def test_load_scenarios_git_rev_parse_failure(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """_load_scenarios warns when the directory is not a git repository.

    Args:
        caplog: pytest log capture fixture
    """
    from pytest_ansible.plugin import _load_scenarios

    config = MagicMock()
    config.rootpath.as_posix.return_value = "/tmp/not-a-repo"  # noqa: S108
    failed = MagicMock(returncode=1, stdout="", stderr="not a git repo")

    with (
        patch("pytest_ansible.plugin.shutil.which", return_value="/usr/bin/git"),
        patch("pytest_ansible.plugin.subprocess.run", return_value=failed),
        caplog.at_level(logging.WARNING, logger="pytest_ansible.plugin"),
    ):
        _load_scenarios(config)

    assert "Unable to find git root" in caplog.text
