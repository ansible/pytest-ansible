# -*- coding: utf-8 -*-
import logging
from fnmatch import fnmatch
try:
    from _pytest.main import EXIT_OK, EXIT_NOTESTSCOLLECTED, EXIT_INTERRUPTED  # NOQA
except ImportError:
    from _pytest.main import ExitCode
    EXIT_OK = ExitCode.OK
    EXIT_INTERRUPTED = ExitCode.INTERRUPTED
    EXIT_NOTESTSCOLLECTED = ExitCode.NO_TESTS_COLLECTED

def assert_fnmatch_lines(lines, matches):
    for match in matches:
        for line in lines.split('\n'):
            if line == match or fnmatch(line, match):
                break
        else:
            raise ValueError('String {0} not found in output:\n{1}'.format(match, lines))


def test_debug_logging(testdir, capsys):
    '''verifies pytest-github loads configuration from the default configuration file'''

    # setup logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # create stderr StreamHandler
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    # add handler to logger
    logger.addHandler(sh)

    src = """\
    def test_foo(ansible_module):
        ansible_module.ping()
    """
    result = testdir.inline_runsource(src, *['--ansible-inventory', 'localhost,', '--ansible-connection', 'local',
                                             '--ansible-host-pattern', 'all'])

    # Assert py.test exit code
    assert result.ret == EXIT_OK

    (stdout, stderr) = capsys.readouterr()
    fnmatch_lines = [
        'DEBUG - pytest_addoption() called',
        'DEBUG - pytest_configure() called',
        'DEBUG - pytest_generate_tests() called',
        'DEBUG - PyTestAnsiblePlugin initialized',
        'DEBUG - pytest_collection_modifyitems() called',
        'DEBUG - config: {*',
        'DEBUG - request: {*',
        'DEBUG - pytest_report_header() called',
    ]

    # 'DEBUG - pytest_cmdline_main() called',
    # 'DEBUG - pytest_runtest_setup() called',
    # X log.debug("pytest_addoption() called")
    # X log.debug("pytest_configure() called")
    # X log.debug("pytest_generate_tests() called")
    # X log.debug("PyTestAnsiblePlugin initialized")
    # X log.debug("pytest_report_header() called")
    # X log.debug("pytest_collection_modifyitems() called")
    # log.debug("ansible marker override %s:%s" % (short_key, kwargs[short_key]))
    # # log.debug("kwargs: %s" % kwargs)

    # Assert stderr logging
    assert_fnmatch_lines(stderr, fnmatch_lines)
