from typing import Iterator

from atlascli import AtlasProject
from atlascli.atlascommand import AtlasCommand, CommandType, ResourceType
from atlascli.atlaskey import AtlasKey

class CreateCommand(AtlasCommand):

    def __init__(self,
                 atlas_key:AtlasKey=None):
        self._command_type = CommandType.CREATE
        super().__init__(atlas_key)
        self._class = None
        self._create_func = None

    def command_type(self):
        return self._command_type

    def create(self, identifier, data):
            self._create_func(identifier, data)

    def delete(self, resources:Iterator):
        for i in resources:
            self._delete_func(i)

    def modify(self, resoir):


class CreateProjectCommand(CreateCommand):

    def __init__(self, atlas_key: AtlasKey = None):
        super().__init__(atlas_key)
        self._resource_type = ResourceType.PROJECT
        self._command_type = (CommandType.CREATE, self._resource_type)
        self._class = AtlasProject
        self._create_func = self._api.create_project
