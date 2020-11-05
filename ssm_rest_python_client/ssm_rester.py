import requests

from ssm_rest_python_client.models import DatasetModel

_DATASET_ENDPOINT = "datasets"
_MODELS_ENDPOINT = "models"


class SSMRester:
    def __init__(self, hostname="http://localhost", port=8080):
        """
        Initialize a SSM Rest Client

        Args:
            hostname (str): Hostname for the SSM REST API server
            port (int): Port on the host to use
        """
        self.hostname = hostname
        self.port = port

    def _dataset_endpoint(self, resource=None):
        """
        Helper function to form the address of the `datasets` endpoint

        Args:
            resource (str): Resource in form of UUID to access a give dataset

        Return:
            endpoint (str): Datasets endpoint to use
        """
        endpoint = "{uri}/{dataset}".format(
            uri=self.uri,
            dataset=_DATASET_ENDPOINT)

        if resource:
            endpoint += "/{}".format(resource)
        return endpoint

    @property
    def uri(self):
        """
        URI property for DatasetModel
        """
        return "{host}:{port}".format(host=self.hostname, port=self.port)

    def create_new_dataset(self):
        """
        Create a new dataset at SSM REST API

        Returns:
            dataset (DatasetModel): Created dataset as a DatasetModel object
        """
        response = requests.post(self._dataset_endpoint())
        return DatasetModel(**response.json())

    def get_dataset_by_uuid(self, uuid):
        """
        Get dataset for given UUID at SSM REST API

        Args:
            uuid (str): 64-character UUID for dataset

        Raises:
            DatasetNotFoundException: Raised when we cannot find the Dataset

        Returns:
            dataset (DatasetModel): Dataset with UUID as a DatasetModel object
        """
        response = requests.get(self._dataset_endpoint(uuid))
        response.raise_for_status()
        return DatasetModel(**response.json())

    def delete_dataset_by_uuid(self, uuid):
        """
        Delete the dataset for given UUID at SSM REST API

        Args:
            uuid (str): 64-character UUID for dataset

        Raises:
            DatasetNotFoundException: Raised when we cannot find the Dataset
        """
        response = requests.delete(self._dataset_endpoint(uuid))
        response.raise_for_status()
