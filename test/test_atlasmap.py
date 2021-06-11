import unittest
import os
import pprint

from atlascli.atlasapi import AtlasAPI
from atlascli.atlasmap import AtlasMap


class TestOrganization(unittest.TestCase):
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = AtlasAPI()
        self._api.authenticate()
        self._org = self._api.get_this_organization()
        self._map = AtlasMap(org=self._org, api=self._api)

    def test_is_cluster_name(self):
        self.assertTrue(self._map.is_cluster_name("GDELT"))
        self.assertTrue(self._map.is_cluster_name("covid-19"))
        self.assertTrue(self._map.is_cluster_name("DRA-Data"))
        self.assertTrue(self._map.is_cluster_name("MUGAlyser"))
       
    def test_is_unique(self):
        self.assertTrue(self._map.is_unique_cluster("MUGAlyser"))

    def test_get_project_ids(self):
        self.assertEqual("5a141a774e65811a132a8010", self._map.get_project_ids("MOT")[0])
        x = self._map.get_project_ids("XXXXX")
        self.assertEqual(len(x), 0)

    def test_get_project_id(self):
        id = self._map.get_project_id("Open Data Project")
        self.assertEqual("5a141a774e65811a132a8010", id)

    def test_get_project_name(self):
        name = self._map.get_project_name("5a141a774e65811a132a8010")
        self.assertEqual("Open Data Project", name)
        
    def test_is_projectid(self):
        self.assertTrue(self._map.is_project_id("5a141a774e65811a132a8010"))


if __name__ == '__main__':
    unittest.main()
