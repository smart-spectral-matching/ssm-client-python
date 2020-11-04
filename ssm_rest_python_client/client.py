import requests

_DATASET_ENDPOINT = "datasets"
_MODELS_ENDPOINT = "models"


class SSMClient:
    def __init__(self, hostname="http://localhost", port=8080):
        self.hostname = hostname
        self.port = port

    @property
    def uri(self):
        return "{host}:{port}".format(host=self.hostname, port=self.port)

    def create_new_dataset(self):
        response = requests.post(self.uri + "/" + _DATASET_ENDPOINT)
        return response.content
