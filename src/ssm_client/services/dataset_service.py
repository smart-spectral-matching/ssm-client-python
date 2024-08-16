import requests
import warnings

from ssm_client.containers import DatasetContainer
from .collection_service import _COLLECTION_ENDPOINT

_DATASETS_ENDPOINT = "datasets"

_FORMAT_JSONLD = "jsonld"
_FORMAT_SSM_JSON = "json"
_DATASET_FORMAT_CHOICES = [_FORMAT_JSONLD, _FORMAT_SSM_JSON]


class MismatchedCollectionException(Exception):
    """
    Raised when CollectionContainer title doesn't match
    same title passed in
    """


class UnsupportedDatasetFormatException(Exception):
    """Raised when unsupported dataset format specified"""


class DatasetService:
    def __init__(
        self,
        hostname="http://localhost",
        collection=None,
        collection_title=None,
    ):
        """
        Initialize a DatasetService object

        Args:
            hostname (str): Hostname for the SSM Catalog API server
            collection (CollectionContainer): collection for dataset
            collection_title (str): Title of the collection for dataset

        Raises:
            MistmatchedcollectionException:
                Raised when collection and title do not match
        """
        self.hostname = hostname

        if collection and collection_title:
            if collection.title != collection_title:
                msg = (
                    "collection: {collection_title} and title: {title}"
                    "NOT equal!\n"
                    "Trying using one method, "
                    "either the collection OR the title"
                )
                msg = msg.format(
                    collection_title=collection.title, title=collection_title
                )
                raise MismatchedCollectionException(msg)

        self.collection_title = collection_title
        if collection:
            self.collection_title = collection.title

    def _endpoint(self, dataset=None):
        """
        Helper function to form the address of the `datasets` endpoint

        Args:
            dataset (str): 64-character UUID to access a give dataset

        Returns:
            endpoint (str): Datasets endpoint to use
        """
        endpoint = []
        endpoint.append(f"{self.uri}/{_COLLECTION_ENDPOINT}")
        endpoint.append(f"{self.collection_title}/{_DATASETS_ENDPOINT}")
        if dataset:
            endpoint.append(f"{dataset}")
        return "/".join(endpoint)

    @property
    def uri(self):
        """
        URI property for SSM Catalog API
        """
        return f"{self.hostname}"

    def create(self, dataset):
        """
        Create a new dataset for collection at SSM Catalog API

        Args:
            dataset (dict): JSON-LD Dataset to create for collection

        Raises:
            requests.HTTPError: Raised when we cannot find
                the collection or Dataset

        Returns:
            dataset (DatasetContainer): Created DatasetContainer object
        """
        # Providing warnings for "critical" sections to allow try-catch logic
        # for this function
        if not dataset.get("@graph"):
            msg = 'No "@graph" section found for JSON-LD.'
            warnings.warn(msg)
        else:
            if not dataset.get("@graph").get("title"):
                msg = 'No title found in "@graph" section of JSON-LD.'
                warnings.warn(msg)

        response = requests.post(self._endpoint(), json=dataset)
        response.raise_for_status()
        return DatasetContainer(**response.json())

    def get_by_uuid(self, uuid, format: str = _FORMAT_JSONLD):
        """
        Get dataset for given UUID at SSM Catalog API

        Args:
            uuid (str): 64-character UUID for dataset
            format (str): Choice of format to return.
                Default: "jsonld" Choices: ["json", "jsonld"]

        Raises:
            requests.HTTPError: Raised when we cannot find
                the collection or dataset

        Returns:
            dataset (DatasetContainer): DatasetContainer object with given UUID
        """
        if format not in _DATASET_FORMAT_CHOICES:
            msg = (
                "format: {format} not supported\n"
                "Supported dataset formats are {choices}"
            )
            msg = msg.format(
                format=format,
                choices=_DATASET_FORMAT_CHOICES,
            )
            raise UnsupportedDatasetFormatException(msg)
        params = {"format": format}
        response = requests.get(self._endpoint(uuid), params=params)
        response.raise_for_status()

        output = DatasetContainer()
        if format is _FORMAT_JSONLD:
            output = DatasetContainer(**response.json())
        elif format is _FORMAT_SSM_JSON:
            output = DatasetContainer(dataset=response.json())
        return output

    def replace_dataset_for_uuid(self, uuid, dataset):
        """
        Update via replace Dataset for given UUID at SSM Catalog API

        Args:
            uuid (str): 64-character UUID for dataset to replace
            dataset (dict): JSON-LD for Dataset to replace

        Raises:
            requests.HTTPError: Raised when we cannot find
                the collection or dataset

        Returns:
            new_dataset (DatasetContainer): Updated DatasetContainer object
        """
        response = requests.put(self._endpoint(uuid), json=dataset)
        response.raise_for_status()
        return DatasetContainer(**response.json())

    def update_dataset_for_uuid(self, uuid, dataset):
        """
        Update part of Dataset for given UUID at SSM Catalog API

        Args:
            uuid (str): 64-character UUID for dataset to replace
            dataset (dict): JSON-LD with partial dataset to update

        Raises:
            requests.HTTPError: Raised when we cannot find
                the collection or dataset

        Returns:
            new_dataset (DatasetContainer): Updated DatasetContainer object
        """
        response = requests.patch(self._endpoint(uuid), json=dataset)
        response.raise_for_status()
        return DatasetContainer(**response.json())

    def delete_by_uuid(self, uuid):
        """
        Delete the Dataset for given UUID at SSM Catalog API

        Args:
            uuid (str): 64-character UUID for dataset

        Raises:
            requests.HTTPError: Raised when we cannot find
                the collection or dataset
        """
        response = requests.delete(self._endpoint(uuid))
        response.raise_for_status()
