# Ansible Pytest Documentation

## A note from pytest-ansible

**pytest-ansible is deprecated**, with a planned project end-of-life of
**December 2026**. See the [README](https://github.com/ansible/pytest-ansible#a-note-from-pytest-ansible)
for the full note, migration paths, and thanks to everyone who contributed.

In short:

| What you used | Use instead |
| --- | --- |
| Collection unit tests | [ADE](https://github.com/ansible/ansible-dev-environment) + plain pytest |
| Collection CI matrix | [tox-ansible](https://github.com/ansible/tox-ansible) |
| Molecule scenarios | `molecule test --all` |
| Host iteration / ad-hoc modules in pytest | Copy-paste helpers in the README (parametrize + `ansible` CLI) |

## About Ansible Pytest (legacy)

Until December 2026, the plugin still provides:

1. **Unit Testing for Ansible Collections**: Aids in running unit tests for
   Ansible collections using pytest (prefer ADE for new work).

2. **Ansible Integration for Pytest Tests**: Fixtures such as `ansible_adhoc`
   and `ansible_module` for calling Ansible from pytest (prefer in-repo CLI
   helpers or Molecule).

Molecule scenario integration via pytest-ansible is **deprecated** on a faster
track. Run scenarios with the Molecule CLI (`molecule test --all`) or
tox-ansible instead. See
[Getting started](getting_started.md#molecule-scenario-integration-deprecated).
