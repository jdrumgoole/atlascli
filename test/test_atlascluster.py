import unittest
import pprint
import random
import string

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

    def test_create_delete(self):
        cluster_dict = AtlasCluster.default_single_region_cluster()
        cluster_dict["name"] =AtlasCluster.random_name()
        cluster = AtlasCluster(cluster_dict)
        self.assertEqual(cluster.name, cluster_dict["name"])
        created_cluster= self._api.create_cluster("5a141a774e65811a132a8010", cluster.resource)
        self._api.delete_cluster("5a141a774e65811a132a8010", cluster.name)

    def test_modify(self):
        bi_on = {'biConnector': {'enabled': True, 'readPreference': 'secondary'}}
        self._api.modify_cluster(project_id="5a141a774e65811a132a8010",
                                 cluster_name="demodata",
                                 modifications=bi_on)

        cluster = self._api.get_one_cluster(project_id="5a141a774e65811a132a8010",
                                            cluster_name="demodata")

        self.assertTrue( cluster.resource['biConnector']["enabled"])
        bi_off = {'biConnector': {'enabled': False, 'readPreference': 'secondary'}}
        self._api.modify_cluster(project_id="5a141a774e65811a132a8010",
                                 cluster_name="demodata",
                                 modifications=bi_off)
        cluster = self._api.get_one_cluster(project_id="5a141a774e65811a132a8010",
                                            cluster_name="demodata")

        self.assertFalse( cluster.resource['biConnector']["enabled"])

if __name__ == '__main__':
    unittest.main()
