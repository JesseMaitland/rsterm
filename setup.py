import sys
import os
from setuptools import setup, find_packages
from setuptools.command.install import install

VERSION = '0.0.10'


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(tag, VERSION)
            sys.exit(info)


def readme():
    with open('README.md') as file:
        return file.read()


setup(
    name='rsterm',
    version=VERSION,
    author='Jesse Maitland',
    discription='A simple toolkit for making a cli that interfaces with AWS Redshift',
    include_package_data=True,
    long_description=readme(),
    install_requires=[
        'psycopg2-binary',
        'python-dotenv',
        'pyyaml'
    ],
    license='MIT',
    packages=find_packages(exclude=('tests*', 'venv')),
    entry_points={
        'console_scripts': ['rsterm = rsterm.__main__:main']
    },
    download_url="",
    long_description_content_type="text/markdown",
    python_requires='>=3',
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
