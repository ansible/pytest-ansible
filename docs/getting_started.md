# Getting Started

!!! warning

    **pytest-ansible is deprecated** (project end-of-life: **December 2026**).
    Prefer [ADE](https://github.com/ansible/ansible-dev-environment) + plain
    pytest for collection unit tests, and `molecule test --all` for scenarios.
    See the [README note](https://github.com/ansible/pytest-ansible#a-note-from-pytest-ansible)
    for migration examples (host iteration, in-repo `ansible` helpers).

## Unit Testing for Ansible Collections (legacy)

The `pytest-ansible` plugin allows ansible collection's unit tests to be run
with only `pytest`. It offers a focused approach to testing individual Ansible
modules. With this plugin, you can write and execute unit tests specifically for
Ansible modules, ensuring the accuracy and reliability of your module code. This
is particularly useful for verifying the correctness of module behavior in
isolation.

For new work, prefer `ade install -e` and plain pytest instead of relying on
collection path injection.

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

```toml
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

```shell
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

## Molecule Scenario Integration (deprecated)

!!! warning

    Running Molecule scenarios via pytest-ansible is **deprecated** and will be
    removed in a future release.

Prefer the Molecule CLI (and tox-ansible for collections):

```bash
molecule test --all
# With shared_state collections, use molecule's own concurrency:
molecule test --all --workers 4
```

### Why this is deprecated

pytest-ansible runs each scenario as a separate `molecule test -s <scenario>`
subprocess. That only works for **standalone** scenarios. It does **not**
support Molecule `shared_state` (create once in the default scenario, run
component scenarios, destroy once) or `--workers`. Those require Molecule's
native multi-scenario orchestration.

### Migration

| Old (pytest-ansible) | New |
| --- | --- |
| `molecule_scenario` fixture + glue test file | `molecule test --all` |
| `pytest --molecule` | `molecule test --all` |
| Collection CI via pytest integration env | tox-ansible molecule test type |

The `--molecule*` CLI options, `molecule_scenario` fixture, and
`pytest_ansible.molecule.MoleculeScenario` remain available temporarily but
emit a `DeprecationWarning`.
