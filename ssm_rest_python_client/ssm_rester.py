from ssm_rest_python_client.services import DatasetService, ModelService


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

        self.dataset = DatasetService(hostname=self.hostname, port=self.port)
        self.model = None

    def initialize_model_for_dataset(self, dataset):
        """
        Initialize the Model service for Dataset

        Args:
            dataset (DatasetContainer): Dataset to setup a ModelService for
        """

        self.model = ModelService(
            hostname=self.hostname,
            port=self.port,
            dataset=dataset
        )
