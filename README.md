pytest-ansible
==============

.. image:: https://pypip.in/v/pytest-ansible/badge.png
        :alt: Release Status
        :target: https://pypi.python.org/pypi/pytest-ansible
.. image:: https://pypip.in/d/pytest-ansible/badge.png
        :alt: Downloads
        :target: https://pypi.python.org/pypi/pytest-ansible

This repository contains a plugin for ``py.test`` which allows ansible modules to be used within tests and fixtures.

Installation and Usage
======================
.. code:: python

 py.test --ansible-inventory [path_to_inventory]

This plugin gets automatically connected to ``py.test`` via ``entry point`` if installed.
