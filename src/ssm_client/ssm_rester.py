from ssm_client.services import CollectionService, DatasetService


class SSMRester:
    def __init__(self, hostname: str = "http://localhost"):
        """
        Initialize a SSM Rest Client

        Args:
            hostname (str): Hostname for the SSM REST API server
        """
        self.hostname = hostname

        self.collection = CollectionService(hostname=self.hostname)
        self.dataset = None

    def initialize_dataset_for_collection(self, collection):
        """
        Initialize the Dataset service for collection

        Args:
            collection (CollectionContainer): collection to setup a DatasetService for
        """

        self.dataset = DatasetService(
            hostname=self.hostname,
            collection=collection,
        )
