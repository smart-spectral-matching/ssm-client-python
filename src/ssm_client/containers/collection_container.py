import json


class CollectionContainer:
    def __init__(self, **kwargs):
        self.__title = kwargs.get('title', None)
        self.__uri = kwargs.get('uri', None)

    def __eq__(self, other):
        """
        Support "==" comparison between CollectionContainers

        Args:
            other (CollectionContainer): Collection to compare for equality.

        Return:
            areCollectionsEqual (bool)
        """
        titleEqual = self.title == other.title
        uriEqual = self.uri == other.uri
        return titleEqual and uriEqual

    def __ne__(self, other):
        """
        Support "!=" comparison between CollectionContainers

        Args:
            other (CollectionContainer): Collection to compare for non-equality.

        Return:
            areCollectionsNotEqual (bool)
        """

        titleNotEqual = self.title != other.title
        uriNotEqual = self.uri != other.uri
        return titleNotEqual or uriNotEqual

    def __repr__(self):
        collection_dict = {
            "title": self.title,
            "uri": self.uri,
        }
        return json.dumps(collection_dict)

    def __str__(self):
        fmt = "CollectionContainer(title={title},uri={uri})"
        return fmt.format(title=self.title, uri=self.uri)

    @property
    def title(self):
        """
        Title for CollectionContainer
        """
        return self.__title

    @property
    def uri(self):
        """
        Fuseki server URI / URL where CollectionContainer is stored
        """
        return self.__uri
