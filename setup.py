import os
import sys
import glob
import shutil
from setuptools import setup, Command
from setuptools.command.test import test as TestCommand
from pytest_ansible import __version__, __author__, __author_email__



class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_suite = True
        # self.test_args = '--tb=native --ansible-host-pattern localhost --ansible-inventory inventory'
        self.test_args = '--tb=native --ansible-inventory inventory'

        if self.verbose:
            self.test_args += ' -v'

        if 'PY_ARGS' in os.environ:
            self.test_args += ' ' + os.environ.get('PY_ARGS')

        if 'PK_KEYWORDEXPR' in os.environ:
            self.test_args += ' -k "%s"' % os.environ.get('PY_KEYWORDEXPR')

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded elsewhere
        import pytest
        print "Running: py.test %s" % self.test_args
        sys.path.insert(0, 'lib')
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


setup(
    name="pytest-ansible",
    version=__version__,
    description=__doc__,
    long_description=open('README.md').read(),
    license='MIT',
    keywords='py.test pytest ansible',
    author=__author__,
    author_email=__author_email__,
    url='http://github.com/jlaska/pytest-ansible',
    platforms=['linux', 'osx', 'win32'],
    py_modules=['pytest_ansible'],
    entry_points={
        'pytest11': [
            'pytest-ansible = pytest_ansible'
        ],
    },
    zip_safe=False,
    install_requires=['ansible', 'pytest>=2.2.4'],
    cmdclass={
        'test': PyTest,
        'clean': CleanCommand,
        # 'build_sphinx': BuildSphinx},
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities',
        'Programming Language :: Python',
    ],
)
