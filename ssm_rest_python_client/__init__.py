"""Top-level package for ssm-rest-python-client."""

__author__ = """Marshall McDonnell"""
__email__ = 'mcdonnellmt@ornl.gov'
__version__ = '0.4.0'

from .ssm_rester import SSMRester
from . import io

__all__ = [
    "SSMRester",
    "io",
]
