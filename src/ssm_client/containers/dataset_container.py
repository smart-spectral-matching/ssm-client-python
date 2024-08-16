import json


class DatasetContainer:
    def __init__(self, **kwargs):
        self.__uuid = kwargs.get("uuid", None)
        self.__dataset = kwargs.get("dataset", dict())

    def __eq__(self, other):
        """
        Support "==" comparison between DatasetContainers

        Args:
            other (DatasetContainer): Dataset to compare for equality.

        Return:
            areDatasetsEqual (bool)
        """
        uuidEqual = self.uuid == other.uuid
        datasetEqual = self.dataset == other.dataset
        return uuidEqual and datasetEqual

    def __ne__(self, other):
        """
        Support "!=" comparison between DatasetContainers

        Args:
            other (DatasetContainer): Dataset to compare for non-equality.

        Return:
            areDatasetsNotEqual (bool)
        """

        uuidNotEqual = self.uuid != other.uuid
        datasetNotEqual = self.dataset != other.dataset
        return uuidNotEqual or datasetNotEqual

    def __repr__(self):
        dataset_dict = {
            "uuid": self.uuid,
            "dataset": self.dataset,
        }
        return json.dumps(dataset_dict)

    def __str__(self):
        fmt = "DatasetContainer(\nuuid={uuid},\ndataset={dataset}\n)"
        dataset = json.dumps(self.dataset, sort_keys=True, indent=4)
        return fmt.format(uuid=self.uuid, dataset=dataset)

    @property
    def uuid(self):
        """
        UUID for DatasetContainer
        """
        return self.__uuid

    @property
    def dataset(self):
        """
        JSON-LD for RDF Dataset of the data in DatasetContainer
        """
        return self.__dataset
