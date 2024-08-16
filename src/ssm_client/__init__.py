"""Top-level package for ssm-client."""

__author__ = """Marshall McDonnell"""
__email__ = "mcdonnellmt@ornl.gov"


from .ssm_rester import SSMRester
from . import io


__all__ = [
    "SSMRester",
    "io",
]
