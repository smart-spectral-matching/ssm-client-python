import requests

from ssm_rest_python_client.containers import ModelContainer
from .dataset_service import _DATASETS_ENDPOINT

_MODELS_ENDPOINT = "models"


class MismatchedDatasetException(Exception):
    """Raised when DatasetContainer UUID doesn't match same UUID passed in"""


class ModelService:
    def __init__(
            self,
            hostname="http://localhost",
            port=8080,
            dataset=None,
            dataset_uuid=None):
        """
        Initialize a DatasetService object

        Args:
            hostname (str): Hostname for the SSM REST API server
            port (int): Port on the host to use
            dataset (DatasetContainer): Dataset the Models will belong to
            dataset_uuid (str): UUID of the Dataset the Models will belong to

        Raises:
            MistmatchedDatasetException:
                Raised when Dataset and UUID both passed in and do not match
        """
        self.hostname = hostname
        self.port = port

        if dataset and dataset_uuid:
            if dataset.uuid != dataset_uuid:
                msg = "Dataset: {dataset_uuid} and UUID: {uuid} NOT equal!\n"
                msg = "Trying using one method, either the Dataset OR the UUID"
                msg = msg.format(
                    dataset_uuid=dataset.uuid,
                    uuid=dataset_uuid
                )
                raise MismatchedDatasetException(msg)

        self.dataset_uuid = dataset_uuid
        if dataset:
            self.dataset_uuid = dataset.uuid

    def _endpoint(self, model=None):
        """
        Helper function to form the address of the `models` endpoint

        Args:
            model (str): 64-character UUID to access a give model

        Return:
            endpoint (str): Models endpoint to use
        """
        endpoint = "{uri}/{datasets}/{dataset_uuid}/{models}".format(
            uri=self.uri,
            datasets=_DATASETS_ENDPOINT,
            dataset_uuid=self.dataset_uuid,
            models=_MODELS_ENDPOINT)

        if model:
            endpoint += "/{}".format(model)
        return endpoint

    @property
    def uri(self):
        """
        URI property for SSM REST API
        """
        return "{host}:{port}".format(host=self.hostname, port=self.port)

    def create(self, model):
        """
        Create a new model for Dataset at SSM REST API

        Args:
            model (dict): JSON-LD Model to create for Dataset

        Raises:
            requests.HTTPError: Raised when we cannot find the Dataset or Model

        Returns:
            model (ModelContainer): Created ModelContainer object
        """
        response = requests.post(self._endpoint(), json=model)
        response.raise_for_status()
        return ModelContainer(**response.json())

    def get_by_uuid(self, uuid):
        """
        Get model for given UUID at SSM REST API

        Args:
            uuid (str): 64-character UUID for model

        Raises:
            requests.HTTPError: Raised when we cannot find the Dataset or Model

        Returns:
            model (ModelContainer): ModelContainer object with given UUID
        """
        response = requests.get(self._endpoint(uuid))
        response.raise_for_status()
        return ModelContainer(**response.json())

    def replace_model_for_uuid(self, uuid, model):
        """
        Update via replace Model for given UUID at SSM REST API

        Args:
            uuid (str): 64-character UUID for model to replace
            model (dict): JSON-LD for Model to replace

        Raises:
            requests.HTTPError: Raised when we cannot find the Dataset or Model

        Returns:
            new_model (ModelContainer): Updated ModelContainer object
        """
        response = requests.put(self._endpoint(uuid), json=model)
        response.raise_for_status()
        return ModelContainer(**response.json())

    def update_model_for_uuid(self, uuid, model):
        """
        Update part of Model for given UUID at SSM REST API

        Args:
            uuid (str): 64-character UUID for model to replace
            model (dict): JSON-LD with partial Model to update

        Raises:
            requests.HTTPError: Raised when we cannot find the Dataset or Model

        Returns:
            new_model (ModelContainer): Updated ModelContainer object
        """
        response = requests.patch(self._endpoint(uuid), json=model)
        response.raise_for_status()
        return ModelContainer(**response.json())

    def delete_by_uuid(self, uuid):
        """
        Delete the Model for given UUID at SSM REST API

        Args:
            uuid (str): 64-character UUID for model

        Raises:
            requests.HTTPError: Raised when we cannot find the Dataset or Model
        """
        response = requests.delete(self._endpoint(uuid))
        response.raise_for_status()
