import re
import subprocess
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand
from setuptools import find_packages, Command
try:
    # Python 2 backwards compat
    from __builtin__ import raw_input as input
except ImportError:
    pass


def read_module_contents():
    with open('downstream_cherry_picker/__init__.py') as app_init:
        return app_init.read()


def read_spec_contents():
    with open('downstream-cherry-picker.spec') as spec:
        return spec.read()

module_file = read_module_contents()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))
long_description = open('README.rst').read()
version = metadata['version']


class BumpCommand(Command):
    """ Bump the __version__ number and commit all changes. """

    user_options = [('version=', 'v', 'version number to use')]

    def initialize_options(self):
        new_version = metadata['version'].split('.')
        new_version[-1] = str(int(new_version[-1]) + 1)  # Bump the final part
        self.version = ".".join(new_version)

    def finalize_options(self):
        pass

    def run(self):

        print('old version: %s  new version: %s' %
              (metadata['version'], self.version))
        try:
            input('Press enter to confirm, or ctrl-c to exit >')
        except KeyboardInterrupt:
            raise SystemExit("\nNot proceeding")

        old = "__version__ = '%s'" % metadata['version']
        new = "__version__ = '%s'" % self.version
        module_file = read_module_contents()
        with open('downstream_cherry_picker/__init__.py', 'w') as fileh:
            fileh.write(module_file.replace(old, new))

        old = 'Version:        %s' % metadata['version']
        new = 'Version:        %s' % self.version
        spec_file = read_spec_contents()
        with open('downstream-cherry-picker.spec', 'w') as fileh:
            fileh.write(spec_file.replace(old, new))

        # Commit everything with a standard commit message
        cmd = ['git', 'commit', '-a', '-m', 'version %s' % self.version]
        print(' '.join(cmd))
        subprocess.check_call(cmd)


class ReleaseCommand(Command):
    """ Tag and push a new release. """

    user_options = [('sign', 's', 'GPG-sign the Git tag and release files')]

    def initialize_options(self):
        self.sign = False

    def finalize_options(self):
        pass

    def run(self):
        # Create Git tag
        tag_name = 'v%s' % version
        cmd = ['git', 'tag', '-a', tag_name, '-m', 'version %s' % version]
        if self.sign:
            cmd.append('-s')
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Push Git tag to origin remote
        cmd = ['git', 'push', 'origin', tag_name]
        print(' '.join(cmd))
        subprocess.check_call(cmd)

        # Push master to the remote
        cmd = ['git', 'push', 'origin', 'master']
        print(' '.join(cmd))
        subprocess.check_call(cmd)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main('downstream_cherry_picker --flake8 ' +
                            self.pytest_args)
        sys.exit(errno)


setup(
    name='downstream-cherry-picker',
    description='Cherry-pick GitHub PRs for RH Bugzilla tickets',
    packages=find_packages(exclude=['ez_setup']),
    author='Ken Dreyer',
    author_email='kdreyer [at] redhat.com',
    url='https://github.com/red-hat-storage/downstream-cherry-picker',
    version=metadata['version'],
    license='MIT',
    zip_safe=False,
    keywords='packaging, build, git',
    long_description=long_description,
    scripts=['bin/downstream-cherry-picker'],
    install_requires=[
        'requests',
    ],
    tests_require=[
        'pytest',
        'pytest-flake8',
    ],
    cmdclass={'test': PyTest, 'bump': BumpCommand, 'release': ReleaseCommand},
)
