#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

GITLAB_REPO = 'https://code.ornl.gov/rse/datastreams/ssm/clients'

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = []

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

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
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='ssm_rest_python_client',
    name='ssm_rest_python_client',
    packages=find_packages(
        include=['ssm_rest_python_client', 'ssm_rest_python_client.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url=GITLAB_REPO + 'ssm-rest-python-client.git',
    version='0.1.0',
    zip_safe=False,
)
