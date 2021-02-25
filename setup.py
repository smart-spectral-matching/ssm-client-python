#!/usr/bin/env python

"""The setup script."""

import os
from setuptools import setup, find_packages

THIS_DIR = os.path.dirname(__file__)
GITLAB_REPO = 'https://code.ornl.gov/rse/datastreams/ssm/clients'

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

def read_requirements_from_file(filepath):
    """
    Read a list of requirements from the given file and split into a
    list of strings. It is assumed that the file is a flat
    list with one requirement per line.

    Args:
        filepath:
            Path to the file to read
    Returns:
        A list of strings containing the requirements
    """
    with open(filepath, 'rU') as req_file:
        return req_file.readlines()

setup_args = dict(
    install_requires=read_requirements_from_file(
        os.path.join(
            THIS_DIR,
            'requirements.txt')),
    tests_require=read_requirements_from_file(
        os.path.join(
            THIS_DIR,
            'requirements-dev.txt')),
    setup_requires = ['pytest-runner'])

setup(
    author="Marshall McDonnell",
    author_email='mcdonnellmt@ornl.gov',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Smart Spectral Matching REST API Python Client",
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='ssm_rest_python_client',
    name='ssm_rest_python_client',
    packages=find_packages(
        include=['ssm_rest_python_client', 'ssm_rest_python_client.*']),
    setup_requires=setup_args['setup_requires'],
    install_requires=setup_args['install_requires'],
    tests_require=setup_args['install_requires'] + setup_args['tests_require'],
    test_suite='tests',
    url=GITLAB_REPO + 'ssm-rest-python-client.git',
    version='0.1.0',
    zip_safe=False,
)
