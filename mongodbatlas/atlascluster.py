
from mongodbatlas.atlasresource import AtlasResource


class AtlasCluster(AtlasResource):
    """
    AtlasClusters are created by the API and are never instantiated directly.
    """

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


    def __str__(self):
        quoted_name = f"'{self.name}'"
        if self._resource['paused']:
            state = "paused"
        else:
            state = "running"

        return f"id:'{self.id}' name:{quoted_name:24} state={state}"




