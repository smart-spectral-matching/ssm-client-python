import requests
import warnings

from ssm_rest_python_client.containers import ModelContainer
from .dataset_service import _DATASETS_ENDPOINT

_MODELS_ENDPOINT = "models"


class MismatchedDatasetException(Exception):
    """Raised when DatasetContainer title doesn't match same title passed in"""


class ModelService:
    def __init__(
            self,
            hostname="http://localhost",
            dataset=None,
            dataset_title=None):
        """
        Initialize a DatasetService object

        Args:
            hostname (str): Hostname for the SSM REST API server
            dataset (DatasetContainer): Dataset the Models will belong to
            dataset_title (str): Title of the Dataset the Models will belong to

        Raises:
            MistmatchedDatasetException:
                Raised when Dataset and title both passed in and do not match
        """
        self.hostname = hostname

        if dataset and dataset_title:
            if dataset.title != dataset_title:
                msg = (
                    "Dataset: {dataset_title} and title: {title} NOT equal!\n"
                    "Trying using one method, either the Dataset OR the title"
                )
                msg = msg.format(
                    dataset_title=dataset.title,
                    title=dataset_title
                )
                raise MismatchedDatasetException(msg)

        self.dataset_title = dataset_title
        if dataset:
            self.dataset_title = dataset.title

    def _endpoint(self, model=None):
        """
        Helper function to form the address of the `models` endpoint

        Args:
            model (str): 64-character UUID to access a give model

        Returns:
            endpoint (str): Models endpoint to use
        """
        endpoint = []
        endpoint.append(f'{self.uri}/{_DATASETS_ENDPOINT}')
        endpoint.append(f'{self.dataset_title}/{_MODELS_ENDPOINT}')
        if model:
            endpoint.append(f'/{model}')
        return '/'.join(endpoint)

    @property
    def uri(self):
        """
        URI property for SSM REST API
        """
        return f'{self.hostname}'

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
        # Providing warnings for "critical" sections to allow try-catch logic
        # for this function
        if not model.get("@graph"):
            msg = 'No "@graph" section found for JSON-LD.'
            warnings.warn(msg)
        else:
            if not model.get("@graph").get("title"):
                msg = 'No title found in "@graph" section of JSON-LD.'
                warnings.warn(msg)

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
