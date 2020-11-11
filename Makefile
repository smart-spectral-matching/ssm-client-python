.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 ssm_rest_python_client tests

test: ## run tests quickly with the default Python
	pytest

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source ssm_rest_python_client -m pytest
	coverage report -m
	coverage html
	#$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/ssm_rest_python_client.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ ssm_rest_python_client
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	#$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

## package and upload a release using a ~/.pypirc file
##   requires a .pypirc file w/ ${PROJECT_NAME} defined:
##		- Reference: https://code.ornl.gov/help/user/packages/pypi_repository/index.md
##		- PROJECT_NAME is of the form "code-ssm-python-client"
release-use-pypirc: dist
	twine upload --repository code-ssm-python-client dist/*

## package and upload a release using twine environment variables and project url
##   requires TWINE_USERNAME, TWINE_PASSWORD, and PROJECT_URL variables set:
##		- Reference: https://docs.gitlab.com/ee/user/packages/pypi_repository/#authenticate-with-a-ci-job-token)
##		- PROJECT_URL is of the form https://gitlab.example.com/api/v4/projects/${CI_PROJECT_ID}/packages/pypi
release-use-url: dist
	twine upload --verbose --repository-url $(PROJECT_URL) dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

bumpversion-patch:  ## bump the patch version
	bump2version patch
	##git push
	##git push --tags
