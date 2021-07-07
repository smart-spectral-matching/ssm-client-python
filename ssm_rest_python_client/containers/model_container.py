import json


class ModelContainer:
    def __init__(self, **kwargs):
        self.__uuid = kwargs.get('uuid', None)
        self.__model = kwargs.get('model', dict())

    def __eq__(self, other):
        """
        Support "==" comparison between ModelContainers

        Args:
            other (ModelContainer): Model to compare for equality.

        Return:
            areModelsEqual (bool)
        """
        uuidEqual = self.uuid == other.uuid
        modelEqual = self.model == other.model
        return uuidEqual and modelEqual

    def __ne__(self, other):
        """
        Support "!=" comparison between ModelContainers

        Args:
            other (ModelContainer): Model to compare for non-equality.

        Return:
            areModelsNotEqual (bool)
        """

        uuidNotEqual = self.uuid != other.uuid
        modelNotEqual = self.model != other.model
        return uuidNotEqual or modelNotEqual

    def __repr__(self):
        model_dict = {
            "uuid": self.uuid,
            "model": self.model,
        }
        return json.dumps(model_dict)

    def __str__(self):
        fmt = "ModelContainer(\nuuid={uuid},\nmodel={model}\n)"
        model = json.dumps(self.model, sort_keys=True, indent=4)
        return fmt.format(uuid=self.uuid, model=model)

    @property
    def uuid(self):
        """
        UUID for ModelContainer
        """
        return self.__uuid

    @property
    def model(self):
        """
        JSON-LD for RDF Model of the data in ModelContainer
        """
        return self.__model
