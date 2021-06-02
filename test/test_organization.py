import unittest
import os
import pprint

from atlascli.atlasorganization import AtlasOrganization


class TestOrganization(unittest.TestCase):
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._org = AtlasOrganization()

    def test_is_cluster_name(self):
        self.assertTrue(self._org.is_cluster_name("GDELT"))
        self.assertTrue(self._org.is_cluster_name("covid-19"))
        self.assertTrue(self._org.is_cluster_name("DRA-Data"))
        self.assertTrue(self._org.is_cluster_name("MUGAlyser"))
       
    def test_is_unique(self):
        self.assertTrue(self._org.is_unique("MUGAlyser"))

    def test_get_project_ids(self):
        self.assertEqual( "5a141a774e65811a132a8010", self._org.get_project_ids("MOT")[0])

    def test_get_project_id(self):
        id = self._org.get_project_id("Open Data Project")
        self.assertEqual( "5a141a774e65811a132a8010", id)

    def test_get_project_name(self):
        name = self._org.get_project_name("5a141a774e65811a132a8010")
        self.assertEqual( "Open Data Project", name)
        
    def test_is_projectid(self):
        self.assertTrue(self._org.is_project_id("5a141a774e65811a132a8010"))

if __name__ == '__main__':
    unittest.main()
