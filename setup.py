import os
import glob
import shutil
from ConfigParser import ConfigParser
from setuptools import setup, Command
from setuptools.command.test import test as TestCommand
from pytest_ansible import __version__, __author__, __author_email__


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True

        # read pytest.addopts from setup.cfg
        cp = ConfigParser()
        cp.read('setup.cfg')
        self.test_args = cp.get('pytest', 'addopts')

        # optionally enable verbosity
        if self.verbose:
            self.test_args += ' -v'

        # load additional arguments from PYTEST_ARGS
        if 'PYTEST_ARGS' in os.environ:
            self.test_args += ' ' + os.environ.get('PYTEST_ARGS')

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded elsewhere
        import pytest
        print "Running: py.test %s" % self.test_args
        pytest.main(self.test_args)


class CleanCommand(Command):
    description = "Custom clean command that forcefully removes dist/build directories"
    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd

        # List of things to remove
        rm_list = list()

        # Find any .pyc files or __pycache__ dirs
        for root, dirs, files in os.walk(self.cwd, topdown=False):
            for fname in files:
                if fname.endswith('.pyc') and os.path.isfile(os.path.join(root, fname)):
                    rm_list.append(os.path.join(root, fname))
            if root.endswith('__pycache__'):
                rm_list.append(root)

        # Find egg's
        for egg_dir in glob.glob('*.egg') + glob.glob('*egg-info'):
            rm_list.append(egg_dir)

        # Zap!
        for rm in rm_list:
            if self.verbose:
                print "Removing '%s'" % rm
            if os.path.isdir(rm):
                if not self.dry_run:
                    shutil.rmtree(rm)
            else:
                if not self.dry_run:
                    os.remove(rm)


def long_description(*paths):
    '''Returns a RST formated string.
    '''
    long_description = ''

    # attempt to import pandoc
    try:
        import pypandoc
    except ImportError:
        return long_description

    # attempt md -> rst conversion
    try:
        for path in paths:
            print "PATH: '%s'" % path
            long_description += pypandoc.convert(
                path, 'rst',
                format='markdown'
            )
    except (OSError, IOError):
        return long_description

    return long_description


setup(
    name="pytest-ansible",
    version=__version__,
    description='Plugin for py.test to allow running ansible',
    # long_description=open('README.md').read(),
    long_description=long_description('README.md', 'HISTORY.md'),
    license='MIT',
    keywords='py.test pytest ansible',
    author=__author__,
    author_email=__author_email__,
    url='http://github.com/jlaska/pytest-ansible',
    platforms='any',
    py_modules=['pytest_ansible'],
    entry_points={
        'pytest11': [
            'pytest-ansible = pytest_ansible'
        ],
    },
    zip_safe=False,
    tests_requires=['ansible<2.0', 'pytest>=2.2.4'],
    install_requires=['tox', 'ansible', 'pytest>=2.2.4'],
    cmdclass={
        'test': PyTest,
        'clean': CleanCommand,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7 ',
    ],
)
