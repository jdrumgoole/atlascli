import unittest
import logging
import pprint

from mongodbatlas import AtlasCluster, AtlasOrganization
from mongodbatlas.atlasapi import AtlasAPI
from mongodbatlas.errors import AtlasGetError

class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self._api = AtlasAPI()

    # def test_organization(self):
    #     orig = self._org.create_organization(name="dummy1")
    #     candidate = self._org.get_one_organization(orig.id)
    #     print(f"candidate:{candidate}")
    #     self.assertEqual(orig, candidate)
    #     deleted = AtlasOrganization.delete_organization(candidate.id)
    #     print(f"deleted:{deleted}")

    def test_project(self):
        org = self._api.get_this_organizations()
        created_project = self._api.create_project(org_id=org.id,
                                                   project_name="dummy project")
        read_project = self._api.get_one_project(created_project.id)
        self.assertEqual(created_project, read_project)
        self._api.delete_project(read_project.id)

        with self.assertRaises(AtlasGetError):
            self._api.get_one_project(created_project.id)

    def test_get_one_cluster(self):
        mot_cluster=self._api.get_one_cluster("5a141a774e65811a132a8010", "MOT")
        self.assertEqual(mot_cluster.name, "MOT")

    def test_cluster(self):
        mot_cluster=self._api.get_one_cluster("5a141a774e65811a132a8010", "MOT")
        #self._api.set_logging_level(logging.DEBUG)
        dummy_cluster = mot_cluster
        dummy_cluster.name = "dummy cluster"
        created_cluster = self._api.create_cluster("5a141a774e65811a132a8010", dummy_cluster())
        read_cluster = self._api.get_one_cluster("5a141a774e65811a132a8010", dummy_cluster.name)
        self.assertEqual(dummy_cluster, read_cluster)
        self.api.delete_cluster(dummy_cluster.id)

if __name__ == '__main__':
    unittest.main()
