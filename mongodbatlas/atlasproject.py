from functools import lru_cache

from mongodbatlas.atlasresource import AtlasResource


class AtlasProject(AtlasResource):

    def __init__(self, project=None):
        super().__init__(project)
