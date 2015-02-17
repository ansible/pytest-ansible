pytest-ansible
==============

[![Current Version](https://pypip.in/v/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Supported Python versions](https://pypip.in/py_versions/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Downloads](https://pypip.in/d/pytest-ansible/badge.svg)](https://pypi.python.org/pypi/pytest-ansible/)
[![Build Status](https://travis-ci.org/jlaska/pytest-ansible.png?branch=master)](https://travis-ci.org/jlaska/pytest-ansible)

This repository contains a plugin for ``py.test`` which allows ansible modules to be used within tests and fixtures.

Installation and Usage
======================
.. code:: python

 py.test --ansible-inventory [path_to_inventory]

This plugin gets automatically connected to ``py.test`` via ``entry point`` if installed.
