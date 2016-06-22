import pytest
from pytest_ansible.results import ModuleResult


positive_host_patterns = {
    'all': 2,
    '*': 2,
    'localhost': 1,
    'local*': 1,
    'local*:&*host': 1,
    '!localhost': 1,
    'all[0]': 1,
    'all[-1]': 1,
    '*[0:1]': 2,  # this is confusing, but how host slicing works
    '*[0:]': 2,
}
negative_host_patterns = {
    'none': 0,
    'all[8:]': 0,
}

valid_hosts = ('localhost', 'another_host')
invalid_hosts = ('none', 'all', '*', 'local*')


@pytest.fixture()
def module_result_ok():
    return ModuleResult(**{'invocation': {'module_name': u'debug', 'module_args': {'msg': u'testing'}}, 'msg':
                           u'testing', 'changed': False, '_ansible_verbose_always': True, '_ansible_no_log': False})


@pytest.fixture()
def module_result_failed():
    return ModuleResult(**{'invocation': {'module_name': u'fail', 'module_args': {}}, 'failed': True, 'changed': False,
                           '_ansible_no_log': False, 'msg': u'Failed as requested from task'})


@pytest.fixture()
def module_result_changed():
    return ModuleResult(**{u'changed': True, u'end': u'2016-06-17 21:32:54.877597', '_ansible_no_log': False, u'stdout':
                           u'Fri Jun 17 21:32:54 EDT 2016', u'cmd': [u'date'], u'rc': 0, u'start':
                           u'2016-06-17 21:32:54.873429', u'stderr': u'', u'delta': u'0:00:00.004168', 'invocation':
                           {'module_name': u'command', u'module_args': {u'creates': None, u'executable': None,
                                                                        u'_uses_shell': False, u'_raw_params': u'date',
                                                                        u'removes': None, u'warn': True, u'chdir':
                                                                        None}},
                           'stdout_lines': [u'Fri Jun 17 21:32:54 EDT 2016'], u'warnings': []})


@pytest.fixture()
def module_result_skipped():
    raise NotImplemented("Coming soon!")


@pytest.fixture()
def module_result_unreachable():
    raise NotImplemented("Coming soon!")


@pytest.mark.parametrize(
    "fixture_name,prop",
    [
        ('module_result_ok', 'is_ok'),
        ('module_result_failed', 'is_failed'),
        ('module_result_changed', 'is_changed'),
        pytest.mark.skipif('True')(('module_result_skipped', 'is_skipped')),
        pytest.mark.skipif('True')(('module_result_unreachable', 'is_unreachable')),
    ]
)
def test_is_property(request, fixture_name, prop):
    fixture = request.getfuncargvalue(fixture_name)
    assert getattr(fixture, prop)
