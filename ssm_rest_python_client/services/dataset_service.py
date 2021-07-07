import requests

from ssm_rest_python_client.containers import DatasetContainer

_DATASETS_ENDPOINT = "datasets"


class DatasetService:
    def __init__(self, hostname="http://localhost"):
        """
        Initialize a DatasetService object

        Args:
            hostname (str): Hostname for the SSM REST API server
        """
        self.hostname = hostname

    def _endpoint(self, dataset=None):
        """
        Helper function to form the address of the `datasets` endpoint

        Args:
            dataset (str): title to access a give dataset

        Returns:
            endpoint (str): Datasets endpoint to use
        """
        endpoint = f'{self.uri}/{_DATASETS_ENDPOINT}'
        if dataset:
            endpoint += f'/{dataset}'
        return endpoint

    @property
    def uri(self):
        """
        URI property for DatasetContainer
        """
        return f'{self.hostname}'

    def create(self, title):
        """
        Create a new dataset at SSM REST API

        Args:
            title (str): title for dataset
        Returns:
            dataset (DatasetContainer): Created DatasetContainer object
        """
        json = {"title": title}
        response = requests.post(self._endpoint(), json=json)
        response.raise_for_status()
        return DatasetContainer(**response.json())

    def get_by_title(self, title):
        """
        Get dataset for given title at SSM REST API

        Args:
            title (str): title for dataset

        Raises:
            requests.HTTPError: Raised when we cannot find the Dataset

        Returns:
            dataset (DatasetContainer): DatasetContainer object with given title 
        """
        response = requests.get(self._endpoint(title))
        response.raise_for_status()
        return DatasetContainer(**response.json())

    def delete_by_title(self, title):
        """
        Delete the dataset for given title at SSM REST API

        Args:
            title (str): 64-character title for dataset

        Raises:
            requests.HTTPError: Raised when we cannot find the Dataset
        """
        response = requests.delete(self._endpoint(title))
        response.raise_for_status()
