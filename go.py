F = """

src/pytest_ansible/errors.py:13:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/errors.py:13:24: ANN001 Missing type annotation for function argument `msg`
src/pytest_ansible/errors.py:13:29: ANN001 Missing type annotation for function argument `dark`
src/pytest_ansible/errors.py:13:40: ANN001 Missing type annotation for function argument `contacted`
src/pytest_ansible/fixtures.py:7:5: ANN201 Missing return type annotation for public function `ansible_adhoc`
src/pytest_ansible/fixtures.py:7:19: ANN001 Missing type annotation for function argument `request`
src/pytest_ansible/fixtures.py:11:9: ANN202 Missing return type annotation for private function `init_host_mgr`
src/pytest_ansible/fixtures.py:11:23: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/fixtures.py:18:5: ANN201 Missing return type annotation for public function `ansible_module`
src/pytest_ansible/fixtures.py:18:20: ANN001 Missing type annotation for function argument `ansible_adhoc`
src/pytest_ansible/fixtures.py:25:5: ANN201 Missing return type annotation for public function `ansible_facts`
src/pytest_ansible/fixtures.py:25:19: ANN001 Missing type annotation for function argument `ansible_module`
src/pytest_ansible/fixtures.py:31:5: ANN201 Missing return type annotation for public function `localhost`
src/pytest_ansible/fixtures.py:31:15: ANN001 Missing type annotation for function argument `request`
src/pytest_ansible/fixtures.py:33:101: E501 Line too long (120 > 100)
src/pytest_ansible/host_manager/__init__.py:16:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:16:24: ANN002 Missing type annotation for `*args`
src/pytest_ansible/host_manager/__init__.py:16:25: ARG002 Unused method argument: `args`
src/pytest_ansible/host_manager/__init__.py:16:31: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/host_manager/__init__.py:28:9: ANN202 Missing return type annotation for private function `_default_dispatcher`
src/pytest_ansible/host_manager/__init__.py:28:29: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:28:35: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/host_manager/__init__.py:31:9: ANN201 Missing return type annotation for public function `get_extra_inventory_hosts`
src/pytest_ansible/host_manager/__init__.py:31:35: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:31:41: ANN001 Missing type annotation for function argument `host_pattern`
src/pytest_ansible/host_manager/__init__.py:49:9: ANN201 Missing return type annotation for public function `get_extra_inventory_groups`
src/pytest_ansible/host_manager/__init__.py:49:36: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:57:9: ANN201 Missing return type annotation for public function `check_required_kwargs`
src/pytest_ansible/host_manager/__init__.py:57:31: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:57:37: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/host_manager/__init__.py:57:39: ARG002 Unused method argument: `kwargs`
src/pytest_ansible/host_manager/__init__.py:64:9: ANN201 Missing return type annotation for public function `has_matching_inventory`
src/pytest_ansible/host_manager/__init__.py:64:32: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:64:38: ANN001 Missing type annotation for function argument `host_pattern`
src/pytest_ansible/host_manager/__init__.py:76:9: ANN204 Missing return type annotation for special method `__getitem__`
src/pytest_ansible/host_manager/__init__.py:76:21: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:76:27: ANN001 Missing type annotation for function argument `item`
src/pytest_ansible/host_manager/__init__.py:95:9: ANN204 Missing return type annotation for special method `__getattr__`
src/pytest_ansible/host_manager/__init__.py:95:21: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:95:27: ANN001 Missing type annotation for function argument `attr`
src/pytest_ansible/host_manager/__init__.py:103:9: ANN201 Missing return type annotation for public function `keys`
src/pytest_ansible/host_manager/__init__.py:103:14: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:109:9: ANN204 Missing return type annotation for special method `__iter__`
src/pytest_ansible/host_manager/__init__.py:109:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:122:17: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:128:22: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:128:28: ANN001 Missing type annotation for function argument `item`
src/pytest_ansible/host_manager/__init__.py:132:9: ANN201 Missing return type annotation for public function `initialize_inventory`
src/pytest_ansible/host_manager/__init__.py:132:30: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/__init__.py:138:5: ANN201 Missing return type annotation for public function `get_host_manager`
src/pytest_ansible/host_manager/__init__.py:138:22: ANN002 Missing type annotation for `*args`
src/pytest_ansible/host_manager/__init__.py:138:29: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/host_manager/__init__.py:145:15: TRY003 Avoid specifying long messages outside the exception class
src/pytest_ansible/host_manager/__init__.py:145:28: EM101 Exception must not use a string literal, assign to variable first
src/pytest_ansible/host_manager/v212.py:14:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/v212.py:14:24: ANN002 Missing type annotation for `*args`
src/pytest_ansible/host_manager/v212.py:14:31: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/host_manager/v212.py:19:9: ANN201 Missing return type annotation for public function `initialize_inventory`
src/pytest_ansible/host_manager/v212.py:19:30: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/v213.py:14:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/host_manager/v213.py:14:24: ANN002 Missing type annotation for `*args`
src/pytest_ansible/host_manager/v213.py:14:31: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/host_manager/v213.py:19:9: ANN201 Missing return type annotation for public function `initialize_inventory`
src/pytest_ansible/host_manager/v213.py:19:30: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/__init__.py:13:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/__init__.py:13:24: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/module_dispatcher/__init__.py:20:17: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/__init__.py:32:22: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/__init__.py:32:28: ANN001 Missing type annotation for function argument `item`
src/pytest_ansible/module_dispatcher/__init__.py:33:101: E501 Line too long (111 > 100)
src/pytest_ansible/module_dispatcher/__init__.py:44:9: ANN204 Missing return type annotation for special method `__getattr__`
src/pytest_ansible/module_dispatcher/__init__.py:44:21: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/__init__.py:44:27: ANN001 Missing type annotation for function argument `name`
src/pytest_ansible/module_dispatcher/__init__.py:57:9: ANN201 Missing return type annotation for public function `check_required_kwargs`
src/pytest_ansible/module_dispatcher/__init__.py:57:31: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/__init__.py:57:37: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/module_dispatcher/__init__.py:57:39: ARG002 Unused method argument: `kwargs`
src/pytest_ansible/module_dispatcher/__init__.py:64:9: ANN201 Missing return type annotation for public function `has_module`
src/pytest_ansible/module_dispatcher/__init__.py:64:20: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/__init__.py:64:26: ANN001 Missing type annotation for function argument `name`
src/pytest_ansible/module_dispatcher/__init__.py:64:26: ARG002 Unused method argument: `name`
src/pytest_ansible/module_dispatcher/__init__.py:69:9: ANN202 Missing return type annotation for private function `_run`
src/pytest_ansible/module_dispatcher/__init__.py:69:14: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/__init__.py:69:20: ANN002 Missing type annotation for `*args`
src/pytest_ansible/module_dispatcher/__init__.py:69:21: ARG002 Unused method argument: `args`
src/pytest_ansible/module_dispatcher/__init__.py:69:27: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/module_dispatcher/__init__.py:69:29: ARG002 Unused method argument: `kwargs`
src/pytest_ansible/module_dispatcher/v212.py:29:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v212.py:29:24: ANN002 Missing type annotation for `*args`
src/pytest_ansible/module_dispatcher/v212.py:29:31: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/module_dispatcher/v212.py:35:9: ANN201 Missing return type annotation for public function `v2_runner_on_failed`
src/pytest_ansible/module_dispatcher/v212.py:35:29: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v212.py:35:35: ANN001 Missing type annotation for function argument `result`
src/pytest_ansible/module_dispatcher/v212.py:35:43: ANN002 Missing type annotation for `*args`
src/pytest_ansible/module_dispatcher/v212.py:35:44: ARG002 Unused method argument: `args`
src/pytest_ansible/module_dispatcher/v212.py:35:50: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/module_dispatcher/v212.py:35:52: ARG002 Unused method argument: `kwargs`
src/pytest_ansible/module_dispatcher/v212.py:38:24: SLF001 Private member accessed: `_result`
src/pytest_ansible/module_dispatcher/v212.py:39:24: SLF001 Private member accessed: `_host`
src/pytest_ansible/module_dispatcher/v212.py:41:9: ANN201 Missing return type annotation for public function `v2_runner_on_ok`
src/pytest_ansible/module_dispatcher/v212.py:41:25: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v212.py:41:31: ANN001 Missing type annotation for function argument `result`
src/pytest_ansible/module_dispatcher/v212.py:43:24: SLF001 Private member accessed: `_host`
src/pytest_ansible/module_dispatcher/v212.py:43:51: SLF001 Private member accessed: `_result`
src/pytest_ansible/module_dispatcher/v212.py:45:9: ANN201 Missing return type annotation for public function `v2_runner_on_unreachable`
src/pytest_ansible/module_dispatcher/v212.py:45:34: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v212.py:45:40: ANN001 Missing type annotation for function argument `result`
src/pytest_ansible/module_dispatcher/v212.py:47:26: SLF001 Private member accessed: `_host`
src/pytest_ansible/module_dispatcher/v212.py:47:53: SLF001 Private member accessed: `_result`
src/pytest_ansible/module_dispatcher/v212.py:50:9: ANN201 Missing return type annotation for public function `results`
src/pytest_ansible/module_dispatcher/v212.py:50:17: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v212.py:69:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v212.py:69:24: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/module_dispatcher/v212.py:76:9: ANN201 Missing return type annotation for public function `has_module`
src/pytest_ansible/module_dispatcher/v212.py:76:20: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v212.py:76:26: ANN001 Missing type annotation for function argument `name`
src/pytest_ansible/module_dispatcher/v212.py:90:9: C901 `_run` is too complex (17 > 10)
src/pytest_ansible/module_dispatcher/v212.py:90:9: PLR0912 Too many branches (19 > 12)
src/pytest_ansible/module_dispatcher/v212.py:90:9: PLR0915 Too many statements (66 > 50)
src/pytest_ansible/module_dispatcher/v212.py:90:9: ANN202 Missing return type annotation for private function `_run`
src/pytest_ansible/module_dispatcher/v212.py:90:14: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v212.py:90:20: ANN002 Missing type annotation for `*module_args`
src/pytest_ansible/module_dispatcher/v212.py:90:34: ANN003 Missing type annotation for `**complex_args`
src/pytest_ansible/module_dispatcher/v212.py:101:13: B028 No explicit `stacklevel` keyword argument found
src/pytest_ansible/module_dispatcher/v212.py:132:13: PLW2901 `for` loop variable `argument` overwritten by assignment target
src/pytest_ansible/module_dispatcher/v213.py:38:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v213.py:38:24: ANN002 Missing type annotation for `*args`
src/pytest_ansible/module_dispatcher/v213.py:38:31: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/module_dispatcher/v213.py:44:9: ANN201 Missing return type annotation for public function `v2_runner_on_failed`
src/pytest_ansible/module_dispatcher/v213.py:44:29: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v213.py:44:35: ANN001 Missing type annotation for function argument `result`
src/pytest_ansible/module_dispatcher/v213.py:44:43: ANN002 Missing type annotation for `*args`
src/pytest_ansible/module_dispatcher/v213.py:44:44: ARG002 Unused method argument: `args`
src/pytest_ansible/module_dispatcher/v213.py:44:50: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/module_dispatcher/v213.py:44:52: ARG002 Unused method argument: `kwargs`
src/pytest_ansible/module_dispatcher/v213.py:47:24: SLF001 Private member accessed: `_result`
src/pytest_ansible/module_dispatcher/v213.py:48:24: SLF001 Private member accessed: `_host`
src/pytest_ansible/module_dispatcher/v213.py:50:9: ANN201 Missing return type annotation for public function `v2_runner_on_ok`
src/pytest_ansible/module_dispatcher/v213.py:50:25: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v213.py:50:31: ANN001 Missing type annotation for function argument `result`
src/pytest_ansible/module_dispatcher/v213.py:52:24: SLF001 Private member accessed: `_host`
src/pytest_ansible/module_dispatcher/v213.py:52:51: SLF001 Private member accessed: `_result`
src/pytest_ansible/module_dispatcher/v213.py:54:9: ANN201 Missing return type annotation for public function `v2_runner_on_unreachable`
src/pytest_ansible/module_dispatcher/v213.py:54:34: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v213.py:54:40: ANN001 Missing type annotation for function argument `result`
src/pytest_ansible/module_dispatcher/v213.py:56:26: SLF001 Private member accessed: `_host`
src/pytest_ansible/module_dispatcher/v213.py:56:53: SLF001 Private member accessed: `_result`
src/pytest_ansible/module_dispatcher/v213.py:59:9: ANN201 Missing return type annotation for public function `results`
src/pytest_ansible/module_dispatcher/v213.py:59:17: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v213.py:75:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v213.py:75:24: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/module_dispatcher/v213.py:82:9: ANN201 Missing return type annotation for public function `has_module`
src/pytest_ansible/module_dispatcher/v213.py:82:20: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v213.py:82:26: ANN001 Missing type annotation for function argument `name`
src/pytest_ansible/module_dispatcher/v213.py:96:9: C901 `_run` is too complex (20 > 10)
src/pytest_ansible/module_dispatcher/v213.py:96:9: PLR0912 Too many branches (24 > 12)
src/pytest_ansible/module_dispatcher/v213.py:96:9: PLR0915 Too many statements (76 > 50)
src/pytest_ansible/module_dispatcher/v213.py:96:9: ANN202 Missing return type annotation for private function `_run`
src/pytest_ansible/module_dispatcher/v213.py:96:14: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/module_dispatcher/v213.py:96:20: ANN002 Missing type annotation for `*module_args`
src/pytest_ansible/module_dispatcher/v213.py:96:34: ANN003 Missing type annotation for `**complex_args`
src/pytest_ansible/module_dispatcher/v213.py:111:13: B028 No explicit `stacklevel` keyword argument found
src/pytest_ansible/module_dispatcher/v213.py:147:13: PLW2901 `for` loop variable `argument` overwritten by assignment target
src/pytest_ansible/module_dispatcher/v213.py:250:19: TRY003 Avoid specifying long messages outside the exception class
src/pytest_ansible/module_dispatcher/v213.py:251:17: EM101 Exception must not use a string literal, assign to variable first
src/pytest_ansible/molecule.py:35:5: ANN201 Missing return type annotation for public function `molecule_pytest_configure`
src/pytest_ansible/molecule.py:35:31: ANN001 Missing type annotation for function argument `config`
src/pytest_ansible/molecule.py:50:13: SLF001 Private member accessed: `_metadata`
src/pytest_ansible/molecule.py:54:27: SLF001 Private member accessed: `_metadata`
src/pytest_ansible/molecule.py:55:13: SLF001 Private member accessed: `_metadata`
src/pytest_ansible/molecule.py:56:9: SLF001 Private member accessed: `_metadata`
src/pytest_ansible/molecule.py:64:9: SLF001 Private member accessed: `_metadata`
src/pytest_ansible/molecule.py:96:33: PGH004 Use specific rule codes when using `noqa`
src/pytest_ansible/molecule.py:113:9: ANN201 Missing return type annotation for public function `collect`
src/pytest_ansible/molecule.py:113:17: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/molecule.py:116:16: PLW0603 Using the global statement to update `counter` is discouraged
src/pytest_ansible/molecule.py:123:17: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/molecule.py:134:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/molecule.py:134:24: ANN001 Missing type annotation for function argument `name`
src/pytest_ansible/molecule.py:134:30: ANN001 Missing type annotation for function argument `parent`
src/pytest_ansible/molecule.py:183:21: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/molecule.py:188:9: ANN201 Missing return type annotation for public function `runtest`
src/pytest_ansible/molecule.py:188:17: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/molecule.py:201:21: S603 `subprocess` call: check for execution of untrusted input
src/pytest_ansible/molecule.py:201:21: S607 Starting a process with a partial executable path
src/pytest_ansible/molecule.py:230:21: S603 `subprocess` call: check for execution of untrusted input
src/pytest_ansible/molecule.py:237:25: T201 `print` found
src/pytest_ansible/molecule.py:254:9: ANN201 Missing return type annotation for public function `reportinfo`
src/pytest_ansible/molecule.py:254:20: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/molecule.py:258:17: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/molecule.py:272:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/molecule.py:283:14: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/plugin.py:39:1: B018 Found useless expression. Either assign it to a variable or remove it.
src/pytest_ansible/plugin.py:51:5: ANN201 Missing return type annotation for public function `pytest_addoption`
src/pytest_ansible/plugin.py:51:22: ANN001 Missing type annotation for function argument `parser`
src/pytest_ansible/plugin.py:161:101: E501 Line too long (117 > 100)
src/pytest_ansible/plugin.py:191:5: ANN201 Missing return type annotation for public function `pytest_configure`
src/pytest_ansible/plugin.py:191:22: ANN001 Missing type annotation for function argument `config`
src/pytest_ansible/plugin.py:207:5: S101 Use of `assert` detected
src/pytest_ansible/plugin.py:235:5: ANN201 Missing return type annotation for public function `pytest_generate_tests`
src/pytest_ansible/plugin.py:235:27: ANN001 Missing type annotation for function argument `metafunc`
src/pytest_ansible/plugin.py:247:13: B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
src/pytest_ansible/plugin.py:262:13: B904 Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling
src/pytest_ansible/plugin.py:319:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/plugin.py:319:24: ANN001 Missing type annotation for function argument `config`
src/pytest_ansible/plugin.py:323:9: ANN201 Missing return type annotation for public function `pytest_report_header`
src/pytest_ansible/plugin.py:323:30: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/plugin.py:327:9: ANN201 Missing return type annotation for public function `pytest_collection_modifyitems`
src/pytest_ansible/plugin.py:327:39: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/plugin.py:327:45: ANN001 Missing type annotation for function argument `session`
src/pytest_ansible/plugin.py:327:45: ARG002 Unused method argument: `session`
src/pytest_ansible/plugin.py:327:54: ANN001 Missing type annotation for function argument `config`
src/pytest_ansible/plugin.py:327:62: ANN001 Missing type annotation for function argument `items`
src/pytest_ansible/plugin.py:342:33: SLF001 Private member accessed: `_fixtureinfo`
src/pytest_ansible/plugin.py:343:41: SLF001 Private member accessed: `_fixtureinfo`
src/pytest_ansible/plugin.py:357:9: ANN202 Missing return type annotation for private function `_load_ansible_config`
src/pytest_ansible/plugin.py:357:30: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/plugin.py:357:36: ANN001 Missing type annotation for function argument `config`
src/pytest_ansible/plugin.py:389:9: ANN202 Missing return type annotation for private function `_load_request_config`
src/pytest_ansible/plugin.py:389:30: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/plugin.py:389:36: ANN001 Missing type annotation for function argument `request`
src/pytest_ansible/plugin.py:400:9: ANN201 Missing return type annotation for public function `initialize`
src/pytest_ansible/plugin.py:400:20: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/plugin.py:400:26: ANN001 Missing type annotation for function argument `config`
src/pytest_ansible/plugin.py:400:39: ANN001 Missing type annotation for function argument `request`
src/pytest_ansible/plugin.py:400:53: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/plugin.py:414:9: ANN205 Missing return type annotation for staticmethod `assert_required_ansible_parameters`
src/pytest_ansible/plugin.py:414:44: ANN001 Missing type annotation for function argument `config`
src/pytest_ansible/plugin.py:431:101: E501 Line too long (105 > 100)
src/pytest_ansible/results.py:7:9: ANN202 Missing return type annotation for private function `_check_key`
src/pytest_ansible/results.py:7:20: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:7:26: ANN001 Missing type annotation for function argument `key`
src/pytest_ansible/results.py:14:9: ANN201 Missing return type annotation for public function `is_ok`
src/pytest_ansible/results.py:14:15: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:19:9: ANN201 Missing return type annotation for public function `is_changed`
src/pytest_ansible/results.py:19:20: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:24:9: ANN201 Missing return type annotation for public function `is_unreachable`
src/pytest_ansible/results.py:24:24: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:29:9: ANN201 Missing return type annotation for public function `is_skipped`
src/pytest_ansible/results.py:29:20: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:34:9: ANN201 Missing return type annotation for public function `is_failed`
src/pytest_ansible/results.py:34:19: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:39:9: ANN201 Missing return type annotation for public function `is_successful`
src/pytest_ansible/results.py:39:23: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:47:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:47:24: ANN003 Missing type annotation for `**kwargs`
src/pytest_ansible/results.py:51:13: S101 Use of `assert` detected
src/pytest_ansible/results.py:54:9: ANN204 Missing return type annotation for special method `__getitem__`
src/pytest_ansible/results.py:54:21: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:54:27: ANN001 Missing type annotation for function argument `item`
src/pytest_ansible/results.py:60:9: ANN204 Missing return type annotation for special method `__getattr__`
src/pytest_ansible/results.py:60:21: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:60:27: ANN001 Missing type annotation for function argument `attr`
src/pytest_ansible/results.py:67:17: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:71:22: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:71:28: ANN001 Missing type annotation for function argument `item`
src/pytest_ansible/results.py:75:9: ANN204 Missing return type annotation for special method `__iter__`
src/pytest_ansible/results.py:75:18: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:79:9: ANN201 Missing return type annotation for public function `keys`
src/pytest_ansible/results.py:79:14: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:83:9: ANN201 Missing return type annotation for public function `items`
src/pytest_ansible/results.py:83:15: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/results.py:84:101: E501 Line too long (103 > 100)
src/pytest_ansible/results.py:88:9: ANN201 Missing return type annotation for public function `values`
src/pytest_ansible/results.py:88:16: ANN101 Missing type annotation for `self` in method
src/pytest_ansible/units.py:49:9: TRY400 Use `logging.exception` instead of `logging.error`
src/pytest_ansible/units.py:56:9: TRY400 Use `logging.exception` instead of `logging.error`
src/pytest_ansible/units.py:152:9: SLF001 Private member accessed: `_install`
src/pytest_ansible/units.py:154:51: SLF001 Private member accessed: `_n_configured_paths`
src/pytest_ansible/units.py:162:101: E501 Line too long (116 > 100)
tests/conftest.py:1:1: INP001 File `tests/conftest.py` is part of an implicit namespace package. Add an `__init__.py`.
tests/conftest.py:1:1: D100 Missing docstring in public module
tests/conftest.py:98:5: ANN201 Missing return type annotation for public function `pytest_runtest_setup`
tests/conftest.py:98:5: D103 Missing docstring in public function
tests/conftest.py:98:26: ANN001 Missing type annotation for function argument `item`
tests/conftest.py:116:9: D107 Missing docstring in `__init__`
tests/conftest.py:116:18: ANN101 Missing type annotation for `self` in method
tests/conftest.py:116:24: ANN001 Missing type annotation for function argument `config`
tests/conftest.py:116:32: ANN001 Missing type annotation for function argument `pytester`
tests/conftest.py:145:9: ANN201 Missing return type annotation for public function `args`
tests/conftest.py:145:9: D102 Missing docstring in public method
tests/conftest.py:145:14: ANN101 Missing type annotation for `self` in method
tests/conftest.py:150:5: ANN202 Missing return type annotation for private function `_clear_global_context`
tests/conftest.py:158:5: ANN201 Missing return type annotation for public function `option`
tests/conftest.py:158:12: ANN001 Missing type annotation for function argument `request`
tests/conftest.py:158:21: ANN001 Missing type annotation for function argument `pytester`
tests/conftest.py:159:5: D205 1 blank line required between summary line and description
tests/conftest.py:166:5: ANN201 Missing return type annotation for public function `hosts`
tests/conftest.py:166:5: D103 Missing docstring in public function
tests/conftest.py:167:9: ANN202 Missing return type annotation for private function `create_host_manager`
tests/conftest.py:167:29: FBT002 Boolean default positional argument in function definition
tests/conftest.py:167:29: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/integration/test_molecule.py:22:13: S607 Starting a process with a partial executable path
tests/integration/test_molecule.py:45:31: PLR2004 Magic value used in comparison, consider replacing `4` with a constant variable
tests/integration/test_molecule.py:54:101: E501 Line too long (101 > 100)
tests/test_adhoc.py:1:1: INP001 File `tests/test_adhoc.py` is part of an implicit namespace package. Add an `__init__.py`.
tests/test_adhoc.py:1:1: D100 Missing docstring in public module
tests/test_adhoc.py:24:5: ANN201 Missing return type annotation for public function `test_contacted_with_params`
tests/test_adhoc.py:24:32: ANN001 Missing type annotation for function argument `pytester`
tests/test_adhoc.py:24:42: ANN001 Missing type annotation for function argument `option`
tests/test_adhoc.py:54:5: ANN201 Missing return type annotation for public function `test_contacted_with_params_and_inventory_marker`
tests/test_adhoc.py:54:53: ANN001 Missing type annotation for function argument `pytester`
tests/test_adhoc.py:54:63: ANN001 Missing type annotation for function argument `option`
tests/test_adhoc.py:80:5: ANN201 Missing return type annotation for public function `test_contacted_with_params_and_host_pattern_marker`
tests/test_adhoc.py:80:56: ANN001 Missing type annotation for function argument `pytester`
tests/test_adhoc.py:80:66: ANN001 Missing type annotation for function argument `option`
tests/test_adhoc.py:111:5: ANN201 Missing return type annotation for public function `test_contacted_with_params_and_inventory_host_pattern_marker`
tests/test_adhoc.py:111:66: ANN001 Missing type annotation for function argument `pytester`
tests/test_adhoc.py:111:76: ANN001 Missing type annotation for function argument `option`
tests/test_adhoc.py:142:5: ANN201 Missing return type annotation for public function `test_become`
tests/test_adhoc.py:142:17: ANN001 Missing type annotation for function argument `pytester`
tests/test_adhoc.py:142:27: ANN001 Missing type annotation for function argument `option`
tests/test_adhoc.py:143:5: D205 1 blank line required between summary line and description
tests/test_adhoc.py:169:101: E501 Line too long (119 > 100)
tests/test_adhoc.py:178:10: RUF005 Consider iterable unpacking instead of concatenation
tests/test_adhoc.py:194:5: ANN201 Missing return type annotation for public function `test_dark_with_params`
tests/test_adhoc.py:194:27: ANN001 Missing type annotation for function argument `pytester`
tests/test_adhoc.py:194:37: ANN001 Missing type annotation for function argument `option`
tests/test_adhoc.py:224:5: ANN201 Missing return type annotation for public function `test_dark_with_params_and_inventory_marker`
tests/test_adhoc.py:224:48: ANN001 Missing type annotation for function argument `pytester`
tests/test_adhoc.py:224:58: ANN001 Missing type annotation for function argument `option`
tests/test_adhoc.py:250:5: ANN201 Missing return type annotation for public function `test_dark_with_params_and_host_pattern_marker`
tests/test_adhoc.py:250:51: ANN001 Missing type annotation for function argument `pytester`
tests/test_adhoc.py:250:61: ANN001 Missing type annotation for function argument `option`
tests/test_adhoc.py:282:5: ANN201 Missing return type annotation for public function `test_dark_with_debug_enabled`
tests/test_adhoc.py:282:34: ANN001 Missing type annotation for function argument `pytester`
tests/test_adhoc.py:282:44: ANN001 Missing type annotation for function argument `option`
tests/test_adhoc_result.py:1:1: INP001 File `tests/test_adhoc_result.py` is part of an implicit namespace package. Add an `__init__.py`.
tests/test_adhoc_result.py:1:1: D100 Missing docstring in public module
tests/test_adhoc_result.py:18:5: ANN201 Missing return type annotation for public function `adhoc_result`
tests/test_adhoc_result.py:18:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:18:18: ANN001 Missing type annotation for function argument `request`
tests/test_adhoc_result.py:18:27: ANN001 Missing type annotation for function argument `hosts`
tests/test_adhoc_result.py:19:9: ANN202 Missing return type annotation for private function `create_hosts`
tests/test_adhoc_result.py:26:5: ANN201 Missing return type annotation for public function `test_len`
tests/test_adhoc_result.py:26:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:26:14: ANN001 Missing type annotation for function argument `adhoc_result`
tests/test_adhoc_result.py:33:5: ANN201 Missing return type annotation for public function `test_keys`
tests/test_adhoc_result.py:33:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:33:15: ANN001 Missing type annotation for function argument `adhoc_result`
tests/test_adhoc_result.py:40:5: ANN201 Missing return type annotation for public function `test_items`
tests/test_adhoc_result.py:40:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:40:16: ANN001 Missing type annotation for function argument `adhoc_result`
tests/test_adhoc_result.py:45:9: B007 Loop control variable `count` not used within loop body
tests/test_adhoc_result.py:52:5: ANN201 Missing return type annotation for public function `test_values`
tests/test_adhoc_result.py:52:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:52:17: ANN001 Missing type annotation for function argument `adhoc_result`
tests/test_adhoc_result.py:59:9: B007 Loop control variable `count` not used within loop body
tests/test_adhoc_result.py:65:5: ANN201 Missing return type annotation for public function `test_contains`
tests/test_adhoc_result.py:65:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:65:19: ANN001 Missing type annotation for function argument `adhoc_result`
tests/test_adhoc_result.py:65:33: ANN001 Missing type annotation for function argument `host`
tests/test_adhoc_result.py:74:5: ANN201 Missing return type annotation for public function `test_not_contains`
tests/test_adhoc_result.py:74:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:74:23: ANN001 Missing type annotation for function argument `adhoc_result`
tests/test_adhoc_result.py:74:37: ANN001 Missing type annotation for function argument `host`
tests/test_adhoc_result.py:80:5: ANN201 Missing return type annotation for public function `test_getitem`
tests/test_adhoc_result.py:80:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:80:18: ANN001 Missing type annotation for function argument `adhoc_result`
tests/test_adhoc_result.py:80:32: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_adhoc_result.py:91:5: ANN201 Missing return type annotation for public function `test_not_getitem`
tests/test_adhoc_result.py:91:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:91:22: ANN001 Missing type annotation for function argument `adhoc_result`
tests/test_adhoc_result.py:91:36: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_adhoc_result.py:98:5: ANN201 Missing return type annotation for public function `test_getattr`
tests/test_adhoc_result.py:98:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:98:18: ANN001 Missing type annotation for function argument `adhoc_result`
tests/test_adhoc_result.py:98:32: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_adhoc_result.py:108:5: ANN201 Missing return type annotation for public function `test_not_getattr`
tests/test_adhoc_result.py:108:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:108:22: ANN001 Missing type annotation for function argument `adhoc_result`
tests/test_adhoc_result.py:108:36: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_adhoc_result.py:116:5: ANN201 Missing return type annotation for public function `test_connection_failure_v2`
tests/test_adhoc_result.py:116:5: D103 Missing docstring in public function
tests/test_adhoc_result.py:140:5: ANN201 Missing return type annotation for public function `test_connection_failure_extra_inventory_v2`
tests/test_adhoc_result.py:140:5: D103 Missing docstring in public function
tests/test_fixtures.py:1:1: INP001 File `tests/test_fixtures.py` is part of an implicit namespace package. Add an `__init__.py`.
tests/test_fixtures.py:1:1: D100 Missing docstring in public module
tests/test_fixtures.py:5:39: PGH003 Use specific rule codes when ignoring type issues
tests/test_fixtures.py:12:5: ANN201 Missing return type annotation for public function `test_ansible_adhoc`
tests/test_fixtures.py:12:5: D103 Missing docstring in public function
tests/test_fixtures.py:12:24: ANN001 Missing type annotation for function argument `pytester`
tests/test_fixtures.py:12:34: ANN001 Missing type annotation for function argument `option`
tests/test_fixtures.py:35:5: ANN201 Missing return type annotation for public function `test_ansible_module`
tests/test_fixtures.py:35:5: D103 Missing docstring in public function
tests/test_fixtures.py:35:25: ANN001 Missing type annotation for function argument `pytester`
tests/test_fixtures.py:35:35: ANN001 Missing type annotation for function argument `option`
tests/test_fixtures.py:56:5: ANN201 Missing return type annotation for public function `test_ansible_facts`
tests/test_fixtures.py:56:5: D103 Missing docstring in public function
tests/test_fixtures.py:56:24: ANN001 Missing type annotation for function argument `pytester`
tests/test_fixtures.py:56:34: ANN001 Missing type annotation for function argument `option`
tests/test_fixtures.py:77:5: ANN201 Missing return type annotation for public function `test_localhost`
tests/test_fixtures.py:77:5: D103 Missing docstring in public function
tests/test_fixtures.py:77:20: ANN001 Missing type annotation for function argument `pytester`
tests/test_fixtures.py:77:30: ANN001 Missing type annotation for function argument `option`
tests/test_host_manager.py:1:1: INP001 File `tests/test_host_manager.py` is part of an implicit namespace package. Add an `__init__.py`.
tests/test_host_manager.py:1:1: D100 Missing docstring in public module
tests/test_host_manager.py:23:5: ANN201 Missing return type annotation for public function `test_host_manager_len`
tests/test_host_manager.py:23:5: D103 Missing docstring in public function
tests/test_host_manager.py:23:27: ANN001 Missing type annotation for function argument `hosts`
tests/test_host_manager.py:23:34: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_host_manager.py:34:5: ANN201 Missing return type annotation for public function `test_host_manager_keys`
tests/test_host_manager.py:34:5: D103 Missing docstring in public function
tests/test_host_manager.py:34:28: ANN001 Missing type annotation for function argument `hosts`
tests/test_host_manager.py:34:35: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_host_manager.py:50:5: ANN201 Missing return type annotation for public function `test_host_manager_contains`
tests/test_host_manager.py:50:5: D103 Missing docstring in public function
tests/test_host_manager.py:50:32: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_host_manager.py:50:46: ANN001 Missing type annotation for function argument `num_hosts`
tests/test_host_manager.py:50:46: ARG001 Unused function argument: `num_hosts`
tests/test_host_manager.py:50:57: ANN001 Missing type annotation for function argument `hosts`
tests/test_host_manager.py:50:64: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_host_manager.py:63:5: ANN201 Missing return type annotation for public function `test_host_manager_not_contains`
tests/test_host_manager.py:63:5: D103 Missing docstring in public function
tests/test_host_manager.py:64:5: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_host_manager.py:65:5: ANN001 Missing type annotation for function argument `num_hosts`
tests/test_host_manager.py:65:5: ARG001 Unused function argument: `num_hosts`
tests/test_host_manager.py:66:5: ANN001 Missing type annotation for function argument `hosts`
tests/test_host_manager.py:67:5: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_host_manager.py:81:5: ANN201 Missing return type annotation for public function `test_host_manager_getitem`
tests/test_host_manager.py:81:5: D103 Missing docstring in public function
tests/test_host_manager.py:81:31: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_host_manager.py:81:45: ANN001 Missing type annotation for function argument `num_hosts`
tests/test_host_manager.py:81:45: ARG001 Unused function argument: `num_hosts`
tests/test_host_manager.py:81:56: ANN001 Missing type annotation for function argument `hosts`
tests/test_host_manager.py:81:63: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_host_manager.py:97:5: ANN201 Missing return type annotation for public function `test_host_manager_not_getitem`
tests/test_host_manager.py:97:5: D103 Missing docstring in public function
tests/test_host_manager.py:98:5: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_host_manager.py:99:5: ANN001 Missing type annotation for function argument `num_hosts`
tests/test_host_manager.py:99:5: ARG001 Unused function argument: `num_hosts`
tests/test_host_manager.py:100:5: ANN001 Missing type annotation for function argument `hosts`
tests/test_host_manager.py:101:5: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_host_manager.py:116:5: ANN201 Missing return type annotation for public function `test_host_manager_getattr`
tests/test_host_manager.py:116:5: D103 Missing docstring in public function
tests/test_host_manager.py:116:31: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_host_manager.py:116:45: ANN001 Missing type annotation for function argument `num_hosts`
tests/test_host_manager.py:116:45: ARG001 Unused function argument: `num_hosts`
tests/test_host_manager.py:116:56: ANN001 Missing type annotation for function argument `hosts`
tests/test_host_manager.py:116:63: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_host_manager.py:132:5: ANN201 Missing return type annotation for public function `test_host_manager_slice`
tests/test_host_manager.py:132:5: D103 Missing docstring in public function
tests/test_host_manager.py:132:29: ANN001 Missing type annotation for function argument `host_slice`
tests/test_host_manager.py:132:41: ANN001 Missing type annotation for function argument `num_hosts`
tests/test_host_manager.py:132:52: ANN001 Missing type annotation for function argument `hosts`
tests/test_host_manager.py:132:59: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_host_manager.py:148:5: ANN201 Missing return type annotation for public function `test_host_manager_not_slice`
tests/test_host_manager.py:148:5: D103 Missing docstring in public function
tests/test_host_manager.py:148:33: ANN001 Missing type annotation for function argument `host_slice`
tests/test_host_manager.py:148:45: ANN001 Missing type annotation for function argument `hosts`
tests/test_host_manager.py:148:52: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_host_manager.py:162:5: ANN201 Missing return type annotation for public function `test_host_manager_not_getattr`
tests/test_host_manager.py:162:5: D103 Missing docstring in public function
tests/test_host_manager.py:163:5: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_host_manager.py:164:5: ANN001 Missing type annotation for function argument `num_hosts`
tests/test_host_manager.py:164:5: ARG001 Unused function argument: `num_hosts`
tests/test_host_manager.py:165:5: ANN001 Missing type annotation for function argument `hosts`
tests/test_host_manager.py:166:5: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_host_manager.py:174:5: ANN201 Missing return type annotation for public function `test_defaults`
tests/test_host_manager.py:174:5: D103 Missing docstring in public function
tests/test_host_manager.py:174:19: ANN001 Missing type annotation for function argument `request`
tests/test_module_dispatcher.py:1:1: INP001 File `tests/test_module_dispatcher.py` is part of an implicit namespace package. Add an `__init__.py`.
tests/test_module_dispatcher.py:1:1: D100 Missing docstring in public module
tests/test_module_dispatcher.py:6:5: ANN201 Missing return type annotation for public function `test_runtime_error`
tests/test_module_dispatcher.py:6:5: D103 Missing docstring in public function
tests/test_module_dispatcher.py:18:5: ANN201 Missing return type annotation for public function `test_importerror_requires_v1`
tests/test_module_dispatcher.py:18:5: D103 Missing docstring in public function
tests/test_module_dispatcher.py:21:53: PGH004 Use specific rule codes when using `noqa`
tests/test_module_dispatcher.py:32:5: ANN201 Missing return type annotation for public function `test_dispatcher_len`
tests/test_module_dispatcher.py:32:5: D103 Missing docstring in public function
tests/test_module_dispatcher.py:32:25: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_module_dispatcher.py:32:39: ANN001 Missing type annotation for function argument `num_hosts`
tests/test_module_dispatcher.py:32:50: ANN001 Missing type annotation for function argument `hosts`
tests/test_module_dispatcher.py:32:57: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_module_dispatcher.py:45:5: ANN201 Missing return type annotation for public function `test_dispatcher_contains`
tests/test_module_dispatcher.py:45:5: D103 Missing docstring in public function
tests/test_module_dispatcher.py:45:30: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_module_dispatcher.py:45:44: ANN001 Missing type annotation for function argument `num_hosts`
tests/test_module_dispatcher.py:45:44: ARG001 Unused function argument: `num_hosts`
tests/test_module_dispatcher.py:45:55: ANN001 Missing type annotation for function argument `hosts`
tests/test_module_dispatcher.py:45:62: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_module_dispatcher.py:55:5: ANN201 Missing return type annotation for public function `test_dispatcher_not_contains`
tests/test_module_dispatcher.py:55:5: D103 Missing docstring in public function
tests/test_module_dispatcher.py:56:5: ANN001 Missing type annotation for function argument `host_pattern`
tests/test_module_dispatcher.py:57:5: ANN001 Missing type annotation for function argument `num_hosts`
tests/test_module_dispatcher.py:57:5: ARG001 Unused function argument: `num_hosts`
tests/test_module_dispatcher.py:58:5: ANN001 Missing type annotation for function argument `hosts`
tests/test_module_dispatcher.py:59:5: ANN001 Missing type annotation for function argument `include_extra_inventory`
tests/test_module_dispatcher.py:65:5: ANN201 Missing return type annotation for public function `test_ansible_module_error`
tests/test_module_dispatcher.py:65:31: ANN001 Missing type annotation for function argument `hosts`
tests/test_module_dispatcher.py:73:101: E501 Line too long (114 > 100)
tests/test_module_result.py:1:1: INP001 File `tests/test_module_result.py` is part of an implicit namespace package. Add an `__init__.py`.
tests/test_module_result.py:1:1: D100 Missing docstring in public module
tests/test_module_result.py:28:5: ANN201 Missing return type annotation for public function `module_result_ok`
tests/test_module_result.py:28:5: D103 Missing docstring in public function
tests/test_module_result.py:28:22: ANN001 Missing type annotation for function argument `request`
tests/test_module_result.py:28:22: ARG001 Unused function argument: `request`
tests/test_module_result.py:30:101: E501 Line too long (162 > 100)
tests/test_module_result.py:35:5: ANN201 Missing return type annotation for public function `module_result_failed`
tests/test_module_result.py:35:5: D103 Missing docstring in public function
tests/test_module_result.py:37:101: E501 Line too long (150 > 100)
tests/test_module_result.py:42:5: ANN201 Missing return type annotation for public function `module_result_changed`
tests/test_module_result.py:42:5: D103 Missing docstring in public function
tests/test_module_result.py:42:27: ANN001 Missing type annotation for function argument `request`
tests/test_module_result.py:42:27: ARG001 Unused function argument: `request`
tests/test_module_result.py:44:101: E501 Line too long (221 > 100)
tests/test_module_result.py:60:5: ANN202 Missing return type annotation for private function `_module_result_skipped`
tests/test_module_result.py:66:5: ANN202 Missing return type annotation for private function `_module_result_unreachable`
tests/test_module_result.py:94:5: ANN201 Missing return type annotation for public function `test_is_property`
tests/test_module_result.py:94:5: D103 Missing docstring in public function
tests/test_module_result.py:94:22: ANN001 Missing type annotation for function argument `request`
tests/test_module_result.py:94:31: ANN001 Missing type annotation for function argument `fixture_name`
tests/test_module_result.py:94:45: ANN001 Missing type annotation for function argument `prop`
tests/test_module_result.py:94:51: ANN001 Missing type annotation for function argument `expected_result`
tests/test_params.py:1:1: INP001 File `tests/test_params.py` is part of an implicit namespace package. Add an `__init__.py`.
tests/test_params.py:1:1: D100 Missing docstring in public module
tests/test_params.py:24:5: ANN201 Missing return type annotation for public function `test_plugin_help`
tests/test_params.py:24:22: ANN001 Missing type annotation for function argument `pytester`
tests/test_params.py:39:101: E501 Line too long (101 > 100)
tests/test_params.py:41:101: E501 Line too long (109 > 100)
tests/test_params.py:48:5: ANN201 Missing return type annotation for public function `test_plugin_markers`
tests/test_params.py:48:25: ANN001 Missing type annotation for function argument `pytester`
tests/test_params.py:58:5: ANN201 Missing return type annotation for public function `test_report_header`
tests/test_params.py:58:24: ANN001 Missing type annotation for function argument `pytester`
tests/test_params.py:58:34: ANN001 Missing type annotation for function argument `option`
tests/test_params.py:65:5: ANN201 Missing return type annotation for public function `test_params_not_required_when_not_using_fixture`
tests/test_params.py:65:53: ANN001 Missing type annotation for function argument `pytester`
tests/test_params.py:65:63: ANN001 Missing type annotation for function argument `option`
tests/test_params.py:85:5: ANN201 Missing return type annotation for public function `test_params_required_when_using_fixture`
tests/test_params.py:85:45: ANN001 Missing type annotation for function argument `pytester`
tests/test_params.py:85:55: ANN001 Missing type annotation for function argument `option`
tests/test_params.py:85:63: ANN001 Missing type annotation for function argument `fixture_name`
tests/test_params.py:122:5: ANN201 Missing return type annotation for public function `test_param_requires_value`
tests/test_params.py:122:31: ANN001 Missing type annotation for function argument `pytester`
tests/test_params.py:122:41: ANN001 Missing type annotation for function argument `required_value_parameter`
tests/test_params.py:131:5: ANN201 Missing return type annotation for public function `test_params_required_with_inventory_without_host_pattern`
tests/test_params.py:131:62: ANN001 Missing type annotation for function argument `pytester`
tests/test_params.py:131:72: ANN001 Missing type annotation for function argument `option`
tests/test_params.py:149:5: ANN201 Missing return type annotation for public function `test_params_required_without_inventory_with_host_pattern_v2`
tests/test_params.py:149:5: D103 Missing docstring in public function
tests/test_params.py:149:65: ANN001 Missing type annotation for function argument `pytester`
tests/test_params.py:149:75: ANN001 Missing type annotation for function argument `option`
tests/test_params.py:160:5: ANN201 Missing return type annotation for public function `test_param_override_with_marker`
tests/test_params.py:160:5: D103 Missing docstring in public function
tests/test_params.py:160:37: ANN001 Missing type annotation for function argument `pytester`
tests/test_params.py:160:47: ANN001 Missing type annotation for function argument `option`
tests/test_plugin.py:1:1: INP001 File `tests/test_plugin.py` is part of an implicit namespace package. Add an `__init__.py`.
tests/test_plugin.py:1:1: D100 Missing docstring in public module
tests/test_plugin.py:10:9: D107 Missing docstring in `__init__`
tests/test_plugin.py:10:18: ANN101 Missing type annotation for `self` in method
tests/test_plugin.py:10:24: ANN001 Missing type annotation for function argument `fixturenames`
tests/test_plugin.py:10:38: ANN001 Missing type annotation for function argument `marker`
tests/test_plugin.py:14:9: ANN201 Missing return type annotation for public function `get_closest_marker`
tests/test_plugin.py:14:9: D102 Missing docstring in public method
tests/test_plugin.py:14:28: ANN101 Missing type annotation for `self` in method
tests/test_plugin.py:14:34: ANN001 Missing type annotation for function argument `marker_name`
tests/test_plugin.py:14:34: ARG002 Unused method argument: `marker_name`
tests/test_plugin.py:21:15: RUF012 Mutable class attributes should be annotated with `typing.ClassVar`
tests/test_plugin.py:23:9: ANN201 Missing return type annotation for public function `setoption`
tests/test_plugin.py:23:9: D102 Missing docstring in public method
tests/test_plugin.py:23:19: ANN101 Missing type annotation for `self` in method
tests/test_plugin.py:23:25: ANN001 Missing type annotation for function argument `option_name`
tests/test_plugin.py:23:38: ANN001 Missing type annotation for function argument `value`
tests/test_plugin.py:26:9: ANN201 Missing return type annotation for public function `getoption`
tests/test_plugin.py:26:9: D102 Missing docstring in public method
tests/test_plugin.py:26:19: ANN101 Missing type annotation for `self` in method
tests/test_plugin.py:26:25: ANN001 Missing type annotation for function argument `option_name`
tests/test_plugin.py:29:9: D107 Missing docstring in `__init__`
tests/test_plugin.py:29:18: ANN101 Missing type annotation for `self` in method
tests/test_plugin.py:39:9: ANN201 Missing return type annotation for public function `getplugin`
tests/test_plugin.py:39:9: D102 Missing docstring in public method
tests/test_plugin.py:39:19: ANN101 Missing type annotation for `self` in method
tests/test_plugin.py:39:25: ANN001 Missing type annotation for function argument `name`
tests/test_plugin.py:39:25: ARG002 Unused method argument: `name`
tests/test_plugin.py:46:9: D107 Missing docstring in `__init__`
tests/test_plugin.py:46:18: ANN101 Missing type annotation for `self` in method
tests/test_plugin.py:46:24: ANN001 Missing type annotation for function argument `fixturenames`
tests/test_plugin.py:52:5: ANN201 Missing return type annotation for public function `test_pytest_generate_tests_with_ansible_host`
tests/test_plugin.py:52:5: D103 Missing docstring in public function
tests/test_plugin.py:75:5: ANN201 Missing return type annotation for public function `test_pytest_generate_tests_with_ansible_group`
tests/test_plugin.py:75:5: D103 Missing docstring in public function
tests/test_plugin.py:101:47: PLR2004 Magic value used in comparison, consider replacing `2` with a constant variable
tests/test_plugin.py:104:5: ANN201 Missing return type annotation for public function `test_pytest_collection_modifyitems_with_marker`
tests/test_plugin.py:104:5: D103 Missing docstring in public function
tests/test_plugin.py:123:5: ANN201 Missing return type annotation for public function `test_pytest_collection_modifyitems_without_marker`
tests/test_plugin.py:123:5: D103 Missing docstring in public function
tests/test_plugin.py:138:5: ANN201 Missing return type annotation for public function `test_pytest_collection_modifyitems_no_fixtures`
tests/test_plugin.py:138:5: D103 Missing docstring in public function
tests/unit/test_unit.py:34:34: ARG001 Unused function argument: `start_path`
tests/unit/test_unit.py:84:5: ANN201 Missing return type annotation for public function `test_for_params`
tests/unit/test_unit.py:86:27: S607 Starting a process with a partial executable path
"""

entries = {}
for line in F.splitlines():
    parts = line.split(":")
    filename = parts[0]
    if not filename:
        continue
    if filename not in entries:
        entries[filename] = set()
    oparts = parts[3].split()
    entries[filename].add(oparts[0])

for entry, es in entries.items():
    e = sorted(es)
    print(f'"{entry}" = {e}')
