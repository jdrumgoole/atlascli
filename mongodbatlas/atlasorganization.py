from functools import lru_cache

from mongodbatlas.atlasresource import AtlasResource


class AtlasOrganization(AtlasResource):

    def __init__(self, org=None):
        super().__init__(org)

    def summary_string(self):
        return f"Organization id:'{self.id}' name:'{self.name}'"

