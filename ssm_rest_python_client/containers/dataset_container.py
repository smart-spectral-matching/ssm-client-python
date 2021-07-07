import json


class DatasetContainer:
    def __init__(self, **kwargs):
        self.__title = kwargs.get('title', None)
        self.__uri = kwargs.get('uri', None)

    def __eq__(self, other):
        """
        Support "==" comparison between DatasetContainers

        Args:
            other (DatasetContainer): Dataset to compare for equality.

        Return:
            areDatasetsEqual (bool)
        """
        titleEqual = self.title == other.title
        uriEqual = self.uri == other.uri
        return titleEqual and uriEqual

    def __ne__(self, other):
        """
        Support "!=" comparison between DatasetContainers

        Args:
            other (DatasetContainer): Dataset to compare for non-equality.

        Return:
            areDatasetsNotEqual (bool)
        """

        titleNotEqual = self.title != other.title
        uriNotEqual = self.uri != other.uri
        return titleNotEqual or uriNotEqual

    def __repr__(self):
        dataset_dict = {
            "title": self.title,
            "uri": self.uri,
        }
        return json.dumps(dataset_dict)

    def __str__(self):
        fmt = "DatasetContainer(title={title},uri={uri})"
        return fmt.format(title=self.title, uri=self.uri)

    @property
    def title(self):
        """
        Title for DatasetContainer
        """
        return self.__title

    @property
    def uri(self):
        """
        Fuseki server URI / URL where DatasetContainer is stored
        """
        return self.__uri
