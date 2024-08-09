import requests

from ssm_client.containers import CollectionContainer

_COLLECTION_ENDPOINT = "collections"


class CollectionService:
    def __init__(self, hostname: str = "http://localhost"):
        """
        Initialize a CollectionService object

        Args:
            hostname (str): Hostname for the SSM REST API server
        """
        self.hostname = hostname

    def _endpoint(self, collection: str = "") -> str:
        """
        Helper function to form the address of the `collection` endpoint

        Args:
            collection (str): title to access a give collection

        Returns:
            endpoint (str): Collection endpoint to use
        """
        endpoint = f'{self.uri}/{_COLLECTION_ENDPOINT}'
        if collection:
            endpoint += f'/{collection}'
        return endpoint

    @property
    def uri(self):
        """
        URI property for CollectionContainer
        """
        return f'{self.hostname}'

    def create(self, title: str) -> CollectionContainer:
        """
        Create a new collection at SSM REST API

        Args:
            title (str): title for collection
        Returns:
            collection (CollectionContainer): Created CollectionContainer object
        """
        json = {"title": title}
        response = requests.post(self._endpoint(), json=json)
        response.raise_for_status()
        return CollectionContainer(**response.json())
    
    def get_collections(self) -> list[CollectionContainer]:
        response = requests.get(self._endpoint())
        response.raise_for_status()
        return response.json()

    def get_by_title(self, title: str) -> CollectionContainer:
        """
        Get collection for given title at SSM REST API

        Args:
            title (str): title for collection

        Raises:
            requests.HTTPError: Raised when we cannot find the collection

        Returns:
            collection (CollectionContainer): CollectionContainer object
                with given title
        """
        response = requests.get(self._endpoint(title))
        response.raise_for_status()
        return CollectionContainer(**response.json())

    def delete_by_title(self, title):
        """
        Delete the collection for given title at SSM REST API

        Args:
            title (str): 64-character title for collection

        Raises:
            requests.HTTPError: Raised when we cannot find the collection
        """
        response = requests.delete(self._endpoint(title))
        response.raise_for_status()
