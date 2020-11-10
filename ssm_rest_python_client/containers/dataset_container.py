import json


class DatasetContainer:
    def __init__(self, **kwargs):
        self.__uuid = kwargs.get('uuid', None)
        self.__uri = kwargs.get('uri', None)

    def __eq__(self, other):
        """
        Support "==" comparison between DatasetContainers

        Args:
            other (DatasetContainer): Dataset to compare for equality.

        Return:
            areDatasetsEqual (bool)
        """
        uuidEqual = self.uuid == other.uuid
        uriEqual = self.uri == other.uri
        return uuidEqual and uriEqual

    def __ne__(self, other):
        """
        Support "!=" comparison between DatasetContainers

        Args:
            other (DatasetContainer): Dataset to compare for non-equality.

        Return:
            areDatasetsNotEqual (bool)
        """

        uuidNotEqual = self.uuid != other.uuid
        uriNotEqual = self.uri != other.uri
        return uuidNotEqual or uriNotEqual

    def __repr__(self):
        dataset_dict = {
            "uuid": self.uuid,
            "uri": self.uri,
        }
        return json.dumps(dataset_dict)

    def __str__(self):
        fmt = "DatasetContainer(uuid={uuid},uri={uri})"
        return fmt.format(uuid=self.uuid, uri=self.uri)

    @property
    def uuid(self):
        """
        UUID for DatasetContainer
        """
        return self.__uuid

    @property
    def uri(self):
        """
        Fuseki server URI / URL where DatasetContainer is stored
        """
        return self.__uri
