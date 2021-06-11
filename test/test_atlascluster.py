import os
import unittest
import pprint
import random
import string

from atlascli.atlascluster import AtlasCluster
from atlascli.atlasapi import AtlasAPI
from atlascli.atlasmap import AtlasMap


class TestAtlasCluster(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = AtlasAPI()
        self._api.authenticate()
        self._map = AtlasMap(self._api.get_this_organization(), self._api)

    def test_get_clusters(self):
        clusters = list(self._api.get_clusters("5a141a774e65811a132a8010")) #Open Data Project
        self.assertTrue(len(clusters) > 0)

    def test_atlas_default_cluster(self):
        cluster = AtlasCluster("5a141a774e65811a132a8010", AtlasCluster.default_single_region_cluster())
        self.assertTrue(cluster)

    def test_create_delete(self):
        cluster_dict = AtlasCluster.default_single_region_cluster()
        new_name = AtlasAPI.random_name()
        created_cluster = self._api.create_cluster(project_id="5a141a774e65811a132a8010",
                                                   name=new_name,
                                                   config=cluster_dict)
        self._api.delete_cluster(created_cluster)

    def test_modify(self):
        bi_on = {'biConnector': {'enabled': True, 'readPreference': 'secondary'}}
        cluster = self._api.get_one_cluster(project_id="5a141a774e65811a132a8010", cluster_name="demodata")
        self._api.modify_cluster(cluster,
                                 modifications=bi_on)

        cluster = self._api.get_one_cluster(project_id="5a141a774e65811a132a8010",
                                            cluster_name="demodata")

        #pprint.pprint(cluster)
        self.assertTrue( cluster['biConnector']["enabled"])
        bi_off = {'biConnector': {'enabled': False, 'readPreference': 'secondary'}}
        self._api.modify_cluster(cluster,
                                 modifications=bi_off)
        cluster = self._api.get_one_cluster(project_id="5a141a774e65811a132a8010",
                                            cluster_name="demodata")

        self.assertFalse(cluster['biConnector']["enabled"])

    def test_getcluster(self):
        clusters = self._map.get_cluster("GDELT")
        self.assertEqual(len(clusters), 1)

    def test_dumpload(self):
        clusters = self._map.get_cluster("GDELT")
        AtlasCluster.dump("gdelt.json", clusters[0].resource)
        new_cluster=AtlasCluster.load("gdelt.json")
        self.assertEqual(clusters[0].resource, new_cluster)
        os.unlink("gdelt.json")

    def test_cluster_name(self):
        self.assertTrue(AtlasCluster.is_valid_cluster_name("John"))
        self.assertTrue(AtlasCluster.is_valid_cluster_name("John-Joe"))
        self.assertFalse(AtlasCluster.is_valid_cluster_name("John_Joe"))
if __name__ == '__main__':
    unittest.main()
