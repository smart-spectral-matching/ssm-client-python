import requests
import warnings

from ssm_client.containers import ModelContainer
from .collection_service import _COLLECTION_ENDPOINT

_MODELS_ENDPOINT = "models"


class MismatchedCollectionException(Exception):
    """Raised when CollectionContainer title doesn't match same title passed in"""


class ModelService:
    def __init__(
            self,
            hostname="http://localhost",
            collection=None,
            collection_title=None):
        """
        Initialize a CollectionService object

        Args:
            hostname (str): Hostname for the SSM REST API server
            collection (CollectionContainer): collection the Models will belong to
            collection_title (str): Title of the collection the Models will belong to

        Raises:
            MistmatchedcollectionException:
                Raised when collection and title both passed in and do not match
        """
        self.hostname = hostname

        if collection and collection_title:
            if collection.title != collection_title:
                msg = (
                    "collection: {collection_title} and title: {title} NOT equal!\n"
                    "Trying using one method, either the collection OR the title"
                )
                msg = msg.format(
                    collection_title=collection.title,
                    title=collection_title
                )
                raise MismatchedCollectionException(msg)

        self.collection_title = collection_title
        if collection:
            self.collection_title = collection.title

    def _endpoint(self, model=None):
        """
        Helper function to form the address of the `models` endpoint

        Args:
            model (str): 64-character UUID to access a give model

        Returns:
            endpoint (str): Models endpoint to use
        """
        endpoint = []
        endpoint.append(f'{self.uri}/{_COLLECTION_ENDPOINT}')
        endpoint.append(f'{self.collection_title}/{_MODELS_ENDPOINT}')
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
        Create a new model for collection at SSM REST API

        Args:
            model (dict): JSON-LD Model to create for collection

        Raises:
            requests.HTTPError: Raised when we cannot find the collection or Model

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
            requests.HTTPError: Raised when we cannot find the collection or Model

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
            requests.HTTPError: Raised when we cannot find the collection or Model

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
            requests.HTTPError: Raised when we cannot find the collection or Model

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
            requests.HTTPError: Raised when we cannot find the collection or Model
        """
        response = requests.delete(self._endpoint(uuid))
        response.raise_for_status()
