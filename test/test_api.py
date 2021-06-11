import unittest
import logging
import pprint

from atlascli.atlasapi import AtlasAPI
from atlascli.atlascluster import AtlasCluster
from atlascli.errors import AtlasGetError
from atlascli.outputformat import OutputFormat

import dictdiffer

class TestAPI(unittest.TestCase):

    def setUp(self) -> None:
        self._api = AtlasAPI()
        self._api.authenticate()

    # def test_organization(self):
    #     orig = self._org.create_organization(name="dummy1")
    #     candidate = self._org.get_one_organization(orig.id)
    #     print(f"candidate:{candidate}")
    #     self.assertEqual(orig, candidate)
    #     deleted = AtlasOrganization.delete_organization(candidate.id)
    #     print(f"deleted:{deleted}")

    def test_project(self):
        try:
            org = self._api.get_this_organization()
            # pprint.pprint(org)
            created_project = None
            created_project = self._api.create_project(org_id=org.id,
                                                       project_name="dummy project")
            read_project = self._api.get_one_project(created_project.id)
            # d = dictdiffer.diff(created_project.resource, read_project.resource)
            # pprint.pprint(list(d))
            self.assertEqual(created_project, read_project)
            self._api.delete_project(created_project.id)

            with self.assertRaises(AtlasGetError):
                self._api.get_one_project(created_project.id)
            created_project = None
        finally :
            if created_project:
                self._api.delete_project(created_project.id)


    def test_get_one_cluster(self):
        mot_cluster = self._api.get_one_cluster("5a141a774e65811a132a8010", "MOT")
        # pprint.pprint(mot_cluster)
        self.assertEqual(mot_cluster["name"], "MOT")

    def test_cluster(self):
        mot_cluster = self._api.get_one_cluster("5a141a774e65811a132a8010", "MOT")
        # self._api.set_logging_level(logging.DEBUG)
        dummy_cluster = AtlasCluster.strip_cluster(mot_cluster)
        dummy_cluster.name = AtlasAPI.random_name()
        # dummy_cluster.pprint(fmt=OutputFormat.JSON)
        dummy_cluster["diskSizeGB"] = 60  # m10 clusters have a limit to how much disk space they can use
        created_cluster = self._api.create_cluster("5a141a774e65811a132a8010",
                                                   dummy_cluster.name, dummy_cluster.resource)
        read_cluster = self._api.get_one_cluster("5a141a774e65811a132a8010", dummy_cluster["name"])
        # self.assertEqual(dummy_cluster, read_cluster)
        self._api.delete_cluster(dummy_cluster)


if __name__ == '__main__':
    unittest.main()
