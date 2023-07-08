from ssm_client.services import DatasetService, ModelService


class SSMRester:
    def __init__(self, hostname="http://localhost"):
        """
        Initialize a SSM Rest Client

        Args:
            hostname (str): Hostname for the SSM REST API server
        """
        self.hostname = hostname

        self.dataset = DatasetService(hostname=self.hostname)
        self.model = None

    def initialize_model_for_dataset(self, dataset):
        """
        Initialize the Model service for Dataset

        Args:
            dataset (DatasetContainer): Dataset to setup a ModelService for
        """

        self.model = ModelService(
            hostname=self.hostname,
            dataset=dataset
        )
