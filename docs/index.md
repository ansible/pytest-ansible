# Ansible Pytest Documentation

## About Ansible Pytest

The `pytest-ansible` plugin is designed to provide seamless integration between
`pytest` and `Ansible`, allowing you to efficiently run and test Ansible-related
tasks and scenarios within your pytest test suite. This plugin enhances the
testing workflow by offering these pieces of functionality:

1. **Unit Testing for Ansible Collections**: This feature aids in running unit
   tests for `Ansible collections` using `pytest`. It allows you to validate the
   behavior of your Ansible `modules` and `roles` in isolation, ensuring that
   each component functions as expected.

2. **Ansible Integration for Pytest Tests**: With this functionality, you can
   seamlessly use `Ansible` from within your `pytest` tests. This opens up
   possibilities to interact with Ansible components and perform tasks like
   provisioning resources, testing configurations, and more, all while
   leveraging the power and flexibility of pytest.

Molecule scenario integration via pytest-ansible is **deprecated**. Run scenarios
with the Molecule CLI (`molecule test --all`) or tox-ansible instead. See
[Getting started](getting_started.md#molecule-scenario-integration-deprecated).
