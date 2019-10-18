from pprint import pprint

from mongodbatlas.atlasresource import AtlasResource
from mongodbatlas.apimixin import OutputFormat


class AtlasCluster(AtlasResource):

    @classmethod
    def default_single_region_cluster(cls):
        return {
          #"name" : "DataStore",
          "diskSizeGB" : 100,
          "numShards" : 1,
          "providerSettings" : {
            "providerName" : "AWS",
            "diskIOPS" : 300,
            "instanceSizeName" : "M40",
            "regionName" : "US_EAST_1"
          },
          "replicationFactor" : 3,
          "backupEnabled" : True,
          "autoScaling":{"diskGBEnabled":True},
        }

    def __init__(self, cluster_spec=None):
        super().__init__(cluster_spec)


    def summary_string(self):
        quoted_name = f"'{self.name}'"
        if self._resource['paused']:
            state = "paused"
        else:
            state = "running"
        return f"Cluster      id:'{self.id}' name:{quoted_name:24} {state}"

    def print(self, fmt=OutputFormat.SUMMARY):
        if fmt is OutputFormat.SUMMARY:
            print(self.summary_string())
        else:
            pprint(self._resource)

