# Smart Spectal Matching BATS REST API Python Client Library 

Smart Spectral Matching REST API Python Client

| Branch  | Build | Coverage |
|---------|-------|----------|
| NEXT    | [![NEXT](https://code.ornl.gov/rse/datastreams/ssm/clients/ssm-rest-python-client/badges/next/pipeline.svg)](https://code.ornl.gov/rse/datastreams/ssm/clients/ssm-rest-python-client/-/pipelines/next/latest) | [![coverage report](https://code.ornl.gov/rse/datastreams/ssm/clients/ssm-rest-python-client/badges/next/coverage.svg)](https://code.ornl.gov/rse/datastreams/ssm/clients/ssm-rest-python-client/-/commits/next) |
| PROD    | [![PROD](https://code.ornl.gov/rse/datastreams/ssm/clients/ssm-rest-python-client/badges/main/pipeline.svg)](https://code.ornl.gov/rse/datastreams/ssm/clients/ssm-rest-python-client/-/pipelines/main/latest) | [![coverage report](https://code.ornl.gov/rse/datastreams/ssm/clients/ssm-rest-python-client/badges/main/coverage.svg)](https://code.ornl.gov/rse/datastreams/ssm/clients/ssm-rest-python-client/-/commits/main) |

# Installation

### Using pip
Currently, the PyPI packages are hosted
via [GitLab's PyPIpackage registry](https://docs.gitlab.com/ee/user/packages/pypi_repository/)
and are only available to members of this repository.

To install via [pip](https://pip.pypa.io/en/stable/) from this project's package registry, you can issue the following:
```
python -m pip install --extra-index-url https://__token__:<personal access token>code.ornl.gov/api/v4/projects/8013/packages/pypi/simple ssm-rest-python-client
```

To get the `<personal access token>` for the command above,
follow the [GitLab personal access token docs](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).

### Manually
Clone the repository either via:
 - HTTP:
```
git clone https://code.ornl.gov/rse/datastreams/ssm/clients/ssm-rest-python-client.git
```
 - SSH:
```
git clone git@code.ornl.gov:rse/datastreams/ssm/clients/ssm-rest-python-client.git
```

Create a virtual environment and activate to install the package in the isolated environment:
```
python -m venv <name of env>
source <env>/bin/activate
```

To [install the package from the local source tree into the environment](https://packaging.python.org/tutorials/installing-packages/#installing-from-a-local-src-tree), run:
```
python -m pip install .
```

Or to do so in ["Development Mode"](https://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode), you can run:
```
python -m pip install -e .
```

To deactivate the virtual environment
```
deactivate
```

When finished, remove the virtual environment by deleting the directory:
```
rm -rf <name of env>
```

# Usage
After installation, you can use the two main components of this package for the
following functions:
* [`ssm_rest_python_client.io`](#io-module) - Spectroscopy file format translations
* [`ssm_rest_python_client.SSMRester`](#ssmrester) - REST API client for data management

Also, there are [Jupyter Notebooks](https://jupyter.org/)
in the `tutorials/` directory to help get started
and test files under `tests/data` in different directories.

### IO Module

This module is used to translate to and from different spectroscopy file formats.
The currently supported file formats are:
* [JCAMP-DX](http://jcamp-dx.org/)
* [RRUFF](https://rruff.info/)

The module has two main functions, `read` and `write`.

The `read` function reads in spectroscopy files
and translates them to SciData JSON-LD dictionaries.

The `write` function takes SciData JSON-LD dictionaries
and writes them out in the specified spectroscopy file format.

Example:
```python
from ssm_rest_python_client.io import read, write

# Read in from RRUFF, write out to JCAMP-DX
scidata_dict = read("./tests/data/rruff/raman_studtite.rruff", ioformat="rruff")
write("./raman_studtite.jdx", scidata_dict, ioformat="jcamp")

# Modify SciData JSON-LD and write back out to RRUFF
uid = 'my:example:jsonld'
scidata_dict["@graph"]["uid"] = uid
write("./my_raman_studtite.rruff", scidata_dict, ioformat="rruff")
```

### SSMRester

The `SSMRester` is a REST client for the SSM REST API for storing datasets.

The `SSMRester` is a class and you can create an object by providing
the REST API server information (hostname + port) you want to interact
with for uploading / downloading datasets.

A `dataset` is a collection of individual data you want to store
and a `model` is the individual data you store as a graph.

You must have a `dataset` that a `model` is associated with.

With a `SSMRester` object, you can perform common
Create-Read-Update-Delete (CRUD) tasks for datasets and models.

Example:
```python
import json
from ssm_rest_python_client import SSMRester

rester = SSMRester(hostname="http://ssm.ornl.gov")
dataset = rester.dataset.create()
rester.initialize_model_for_dataset(dataset)

model = rester.model.create(scidata_dict)
print(dataset.uuid)
print(model.uuid)
rester.dataset.delete_by_uuid(dataset.uuid)
```

# Development

### Install via poetry

Install via [poetry](https://python-poetry.org/) with dev dependencies:
```
poetry install
```

Then, run commands via `poetry`:
```
poetry run python -c "import ssm_rest_python_client"
```

### Tests / Linting

#### Flake8 linting
Run linting over the package with [flake8](https://flake8.pycqa.org/en/latest/) via:
```
poetry run flake8 ssm_rest_python_client/ tests/
```

#### Pytest testing
Run tests using [pytest](https://docs.pytest.org/en/stable/):
```
poetry run pytest tests/
```

#### Code coverage

Get code coverage reporting using the [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) plugin:
```
poetry run pytest --cov=ssm_rest_python_client --cov-report=term-missing tests/
```

# Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

# Links
* SSM REST Python Client Project GitLab Repository: [https://code.ornl.gov/rse/datastreams/ssm/clients/ssm-rest-python-client](https://code.ornl.gov/rse/datastreams/ssm/clients/ssm-rest-python-client)
* SSM REST API Project GitLab Repository: [https://code.ornl.gov/rse/datastreams/ssm/backend/ssm-bats-rest-api.git](https://code.ornl.gov/rse/datastreams/ssm/backend/ssm-bats-rest-api.git)

# Licensing
[BSD 3-clause](https://choosealicense.com/licenses/bsd-3-clause/)

