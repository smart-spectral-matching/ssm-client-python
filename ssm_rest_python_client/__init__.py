"""Top-level package for ssm-rest-python-client."""

__author__ = """Marshall McDonnell"""
__email__ = 'mcdonnellmt@ornl.gov'

from importlib import metadata
from .ssm_rester import SSMRester
from . import io

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    __version__ = toml.load("pyproject.toml")["tool"]["poetry"]["version"] + "dev"


__all__ = [
    "SSMRester",
    "io",
]
