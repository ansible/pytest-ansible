import os
import sys
import glob
import shutil
from setuptools import setup, Command, find_packages
from setuptools.command.test import test as TestCommand
from pytest_ansible import __version__, __author__, __author_email__


class ToxTestCommand(TestCommand):

    """Test command which runs tox under the hood."""

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        """Initialize options and set their defaults."""
        TestCommand.initialize_options(self)
        self.tox_args = '--recreate'

    def finalize_options(self):
        """Add options to the test runner (tox)."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Invoke the test runner (tox)."""
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)


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
            if root.endswith('__pycache__') or root.endswith('.cache') or root.endswith('.ansible') or \
               root.endswith('.pytest_cache') or \
               root.endswith('.eggs') or root.endswith('.tox'):
                rm_list.append(root)

        # Find egg's
        for egg_dir in glob.glob('*.egg') + glob.glob('*egg-info'):
            rm_list.append(egg_dir)

        # Zap!
        for rm in rm_list:
            if self.verbose:
                print("Removing '%s'" % rm)
            if os.path.isdir(rm):
                if not self.dry_run:
                    shutil.rmtree(rm)
            else:
                if not self.dry_run:
                    os.remove(rm)


def long_description(*paths):
    '''Returns a RST formated string.
    '''
    result = ''

    # attempt to import pandoc
    try:
        import pypandoc
    except (ImportError, OSError) as e:
        print("Unable to import pypandoc - %s" % e)
        return result

    # attempt md -> rst conversion
    try:
        for path in paths:
            result += '\n' + pypandoc.convert(
                path, 'rst', format='markdown'
            )
    except (OSError, IOError) as e:
        print("Failed to convert with pypandoc - %s" % e)
        return result

    return result


setup(
    name="pytest-ansible",
    version=__version__,
    description='Plugin for py.test to simplify calling ansible modules from tests or fixtures',
    long_description=long_description('README.md', 'HISTORY.md'),
    license='MIT',
    keywords='py.test pytest ansible',
    author=__author__,
    author_email=__author_email__,
    url='http://github.com/jlaska/pytest-ansible',
    platforms='any',
    packages=find_packages(),
    entry_points={
        'pytest11': [
            'pytest-ansible = pytest_ansible.plugin'
        ],
    },
    zip_safe=False,
    tests_require=['tox'],
    # setup_requires=['pypandoc<1.2.0', 'setuptools-markdown'],
    setup_requires=['setuptools-markdown'],
    install_requires=['ansible', 'pytest'],
    cmdclass={
        'test': ToxTestCommand,
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
