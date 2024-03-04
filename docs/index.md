# Ansible Pytest Documentation

## About Ansible Pytest

Ansible Pytest is a plugin for ``py.test`` which adds several fixtures
for running ``ansible`` modules, or inspecting ``ansible_facts``.  While one
can simply call out to ``ansible`` using the ``subprocess`` module, having to
parse stdout to determine the outcome of the operation is unpleasant and prone
to error.  With ``pytest-ansible``, modules return JSON data which you can
inspect and act on, much like with an ansible
[playbook](http://docs.ansible.com/playbooks.html).
