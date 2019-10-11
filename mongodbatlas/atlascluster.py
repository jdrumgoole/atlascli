from pprint import pprint

from mongodbatlas.atlasresource import AtlasResource
from mongodbatlas.apimixin import OutputFormat


class AtlasCluster(AtlasResource):

    def __init__(self, cluster=None):
        super().__init__(cluster)

    def summary_string(self):
        quoted_name = f"'{self.name}'"
        if self._resource['paused']:
            state = "paused"
        else:
            state = "running"
        return f"id:'{self.id}' name:{quoted_name:24} {state}"

    def print_resource(self, fmt=OutputFormat.SUMMARY):
        if fmt is OutputFormat.SUMMARY:
            print(self.summary_string())
        else:
            pprint(self._resource)
