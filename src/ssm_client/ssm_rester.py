from ssm_client.services import CollectionService, ModelService


class SSMRester:
    def __init__(self, hostname: str = "http://localhost"):
        """
        Initialize a SSM Rest Client

        Args:
            hostname (str): Hostname for the SSM REST API server
        """
        self.hostname = hostname

        self.collection = CollectionService(hostname=self.hostname)
        self.model = None

    def initialize_model_for_collection(self, collection):
        """
        Initialize the Model service for collection

        Args:
            collection (CollectionContainer): collection to setup a ModelService for
        """

        self.model = ModelService(
            hostname=self.hostname,
            collection=collection,
        )
