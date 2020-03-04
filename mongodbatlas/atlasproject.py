import pprint

from mongodbatlas.atlasresource import AtlasResource


class AtlasProject(AtlasResource):

    def __init__(self, project:dict=None):
        super().__init__(project)

    def __str__(self):
        return f"Project:\n{pprint.pformat(self._resource)}"





