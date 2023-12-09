# Getting Started

## Unit Testing for Ansible Collections

The `pytest-ansible` plugin allows ansible collection's unit tests to be run
with only `pytest`. It offers a focused approach to testing individual Ansible
modules. With this plugin, you can write and execute unit tests specifically for
Ansible modules, ensuring the accuracy and reliability of your module code. This
is particularly useful for verifying the correctness of module behavior in
isolation.

To use `pytest-ansible`, follow these steps:

1. Install the plugin using [pip]:

```
pip install pytest-ansible
```

2. Ensure you have Python 3.10 or greater, ansible-core, and pytest installed.

3. Depending on your preferred directory structure, you can clone collections
   into the appropriate paths.

   - **Collection Tree Approach**: The preferred approach is to clone the
     collections being developed into it's proper collection tree path. This
     eliminates the need for any symlinks and other collections being developed
     can be cloned into the same tree structure.

     ```
     git clone <repo> collections/ansible_collections/<namespace>/<name>
     ```

     Note: Run `pytest` in the root of the collection directory, adjacent to the
     collection's `galaxy.yml` file.

   - **Shallow Tree Approach**:

     ```
     git clone <repo>
     ```

     Notes:

     - Run `pytest` in the root of the collection directory, adjacent to the
       collection's `galaxy.yml` file.
     - A collections directory will be created in the repository directory, and
       collection content will be linked into it.

4. Execute the unit tests using pytest: `pytest tests`

## Help

The following may be added to the collections' `pyproject.toml` file to limit
warnings and set the default path for the collection's tests

```
[tool.pytest.ini_options]
testpaths = [
    "tests",
]
filterwarnings = [
    'ignore:AnsibleCollectionFinder has already been configured',
]
```

Information from the `galaxy.yml` file is used to build the `collections`
directory structure and link the contents. The `galaxy.yml` file should reflect
the correct collection namespace and name.

One way to detect issues without running the tests is to run:

```
pytest --collect-only
```

The follow errors may be seen:

```
E   ModuleNotFoundError: No module named 'ansible_collections'
```

- Check the `galaxy.yml` file for an accurate namespace and name
- Ensure `pytest` is being run from the collection's root directory, adjacent to
  the `galaxy.yml`

```
HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules
```

## Molecule Scenario Integration

This functionality assists in running Molecule `scenarios` using `pytest`. It
enables pytest discovery of all `molecule.yml` files inside the codebase and
runs them as pytest tests. It allows you to include Molecule scenarios as part
of your pytest test suite, allowing you to thoroughly test your Ansible roles
and playbooks across different scenarios and environments.

## Running molecule scenarios using pytest

Molecule scenarios can be tested using 2 different methods if molecule is
installed.

**Recommended:**

Add a `test_integration.py` file to the `tests/integration` directory of the
ansible collection:

```
"""Tests for molecule scenarios."""
from __future__ import absolute_import, division, print_function

from pytest_ansible.molecule import MoleculeScenario


def test_integration(molecule_scenario: MoleculeScenario) -> None:
    """Run molecule for each scenario.

    :param molecule_scenario: The molecule scenario object
    """
    proc = molecule_scenario.test()
    assert proc.returncode == 0
```

The `molecule_scenario` fixture provides parameterized molecule scenarios
discovered in the collection's `extensions/molecule` directory, as well as other
directories within the collection.

`molecule test -s <scenario>` will be run for each scenario and a completed
subprocess returned from the `test()` call.
