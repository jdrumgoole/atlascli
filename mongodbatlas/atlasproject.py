from functools import lru_cache

from mongodbatlas.atlasresource import AtlasResource


class AtlasProject(AtlasResource):

    def __init__(self, project=None):
        super().__init__(project)

    def summary_string(self):
        return f"Project      id:'{self.id}' name:'{self.name}'"
