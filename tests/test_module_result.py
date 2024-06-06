import pytest  # noqa: INP001, D100

from pytest_ansible.results import ModuleResult


positive_host_patterns = {
    "all": 2,
    "*": 2,
    "localhost": 1,
    "local*": 1,
    "local*:&*host": 1,
    "!localhost": 1,
    "all[0]": 1,
    "all[-1]": 1,
    "*[0:1]": 2,  # this is confusing, but how host slicing works
    "*[0:]": 2,
}
negative_host_patterns = {
    "none": 0,
    "all[8:]": 0,
}

valid_hosts = ("localhost", "another_host")
invalid_hosts = ("none", "all", "*", "local*")


@pytest.fixture()
def module_result_ok(request):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    return ModuleResult(
        invocation={"module_name": "debug", "module_args": {"msg": "testing"}},
        msg="testing",
        changed=False,
        _ansible_verbose_always=True,
        _ansible_no_log=False,
    )


@pytest.fixture()
def module_result_failed():  # type: ignore[no-untyped-def]  # noqa: ANN201, D103
    return ModuleResult(
        invocation={"module_name": "fail", "module_args": {}},
        failed=True,
        changed=False,
        _ansible_no_log=False,
        msg="Failed as requested from task",
    )


@pytest.fixture()
def module_result_changed(request):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, ARG001, D103
    return ModuleResult(
        changed=True,
        end="2016-06-17 21:32:54.877597",
        _ansible_no_log=False,
        stdout="Fri Jun 17 21:32:54 EDT 2016",
        cmd=["date"],
        rc=0,
        start="2016-06-17 21:32:54.873429",
        stderr="",
        delta="0:00:00.004168",
        invocation={
            "module_name": "command",
            "module_args": {
                "creates": None,
                "executable": None,
                "_uses_shell": False,
                "_raw_params": "date",
                "removes": None,
                "warn": True,
                "chdir": None,
            },
        },
        stdout_lines=["Fri Jun 17 21:32:54 EDT 2016"],
        warnings=[],
    )


@pytest.fixture()
def _module_result_skipped():  # type: ignore[no-untyped-def]  # noqa: ANN202
    msg = "Coming soon!"
    raise NotImplementedError(msg)


@pytest.fixture()
def _module_result_unreachable():  # type: ignore[no-untyped-def]  # noqa: ANN202
    msg = "Coming soon!"
    raise NotImplementedError(msg)


@pytest.mark.parametrize(
    ("fixture_name", "prop", "expected_result"),
    (
        ("module_result_ok", "is_ok", True),
        ("module_result_ok", "is_successful", True),
        ("module_result_failed", "is_failed", True),
        ("module_result_failed", "is_successful", False),
        ("module_result_changed", "is_changed", True),
        ("module_result_changed", "is_successful", True),
        pytest.param(
            "module_result_skipped",
            "is_skipped",
            True,
            marks=pytest.mark.skipif("True"),
        ),
        pytest.param(
            "module_result_unreachable",
            "is_unreachable",
            True,
            marks=pytest.mark.skipif("True"),
        ),
    ),
)
def test_is_property(request, fixture_name, prop, expected_result):  # type: ignore[no-untyped-def]  # noqa: ANN001, ANN201, D103
    fixture = request.getfixturevalue(fixture_name)
    assert getattr(fixture, prop) == expected_result
