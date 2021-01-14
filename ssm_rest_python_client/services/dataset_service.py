import requests

from ssm_rest_python_client.containers import DatasetContainer

_DATASETS_ENDPOINT = "datasets"


class DatasetService:
    def __init__(self, hostname="http://localhost", port=8080):
        """
        Initialize a DatasetService object

        Args:
            hostname (str): Hostname for the SSM REST API server
            port (int): Port on the host to use
        """
        self.hostname = hostname
        self.port = port

    def _endpoint(self, dataset=None):
        """
        Helper function to form the address of the `datasets` endpoint

        Args:
            dataset (str): 64-character UUID to access a give dataset

        Returns:
            endpoint (str): Datasets endpoint to use
        """
        endpoint = "{uri}/{dataset}".format(
            uri=self.uri,
            dataset=_DATASETS_ENDPOINT)

        if dataset:
            endpoint += "/{}".format(dataset)
        return endpoint

    @property
    def uri(self):
        """
        URI property for DatasetContainer
        """
        return "{host}:{port}".format(host=self.hostname, port=self.port)

    def create(self):
        """
        Create a new dataset at SSM REST API

        Returns:
            dataset (DatasetContainer): Created DatasetContainer object
        """
        response = requests.post(self._endpoint())
        return DatasetContainer(**response.json())

    def get_by_uuid(self, uuid):
        """
        Get dataset for given UUID at SSM REST API

        Args:
            uuid (str): 64-character UUID for dataset

        Raises:
            requests.HTTPError: Raised when we cannot find the Dataset

        Returns:
            dataset (DatasetContainer): DatasetContainer object with given UUID
        """
        response = requests.get(self._endpoint(uuid))
        response.raise_for_status()
        return DatasetContainer(**response.json())

    def delete_by_uuid(self, uuid):
        """
        Delete the dataset for given UUID at SSM REST API

        Args:
            uuid (str): 64-character UUID for dataset

        Raises:
            requests.HTTPError: Raised when we cannot find the Dataset
        """
        response = requests.delete(self._endpoint(uuid))
        response.raise_for_status()
