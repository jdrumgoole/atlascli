import pprint

from mongodbatlas.atlasresource import AtlasResource


class AtlasProject(AtlasResource):

    def __init__(self, project:dict=None):
        super().__init__(project)

    def summary(self):
        return f"project ID:{self.id} Name:'{self.name}'"

    def __str__(self):
        return f"{pprint.pformat(self._resource)}"





