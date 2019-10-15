import unittest
import pprint

from mongodbatlas.atlascluster import AtlasCluster
from mongodbatlas.atlasresource import AtlasResource
from mongodbatlas.apimixin import APIMixin
from mongodbatlas.api import API


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self._api = API()

    def test_atlasresource(self):
        mixin = APIMixin()
        res = AtlasResource()
        cluster = AtlasCluster()

    def test_create(self):
        cluster_dict = AtlasCluster.default_single_region_cluster()
        cluster_dict["name"] = "testcluster123"
        cluster = AtlasCluster(cluster_dict)
        self.assertEqual(cluster.name, cluster_dict["name"])
        pprint.pprint(cluster.resource)
        self._api.create_cluster("5a141a774e65811a132a8010", cluster.resource)

if __name__ == '__main__':
    unittest.main()
