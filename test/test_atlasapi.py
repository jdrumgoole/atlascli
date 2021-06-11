import unittest
import pprint

from atlascli.atlasapi import AtlasAPI
from atlascli.atlasproject import AtlasProject
from atlascli.errors import AtlasGetError, AtlasError


class TestAtlasAPI(unittest.TestCase):

    def setUp(self) -> None:
        self._api = AtlasAPI()
        self._api.authenticate()

    def test_project(self):
        org = self._api.get_this_organization()
        #pprint.pprint(org)
        created_project = self._api.create_project(org_id=org["id"],
                                                   project_name="dummy project")
        read_project = self._api.get_one_project(created_project["id"])
        self.assertEqual(created_project, read_project)
        self._api.delete_project(read_project["id"])

        with self.assertRaises(AtlasGetError):
            self._api.get_one_project(created_project["id"])

    def test_get_one_cluster(self):
        mot_cluster=self._api.get_one_cluster("5a141a774e65811a132a8010", "MOT")
        #pprint.pprint(mot_cluster)
        self.assertEqual(mot_cluster["name"], "MOT")

    def test_cluster(self):
        mot_cluster=self._api.get_one_cluster("5a141a774e65811a132a8010", "MOT")
        #self._api.set_logging_level(logging.DEBUG)
        dummy_cluster = mot_cluster
        dummy_cluster["name"] = AtlasAPI.random_name()
        del dummy_cluster["connectionStrings"]
        del dummy_cluster["replicationSpecs"]
        del dummy_cluster["mongoURI"]
        del dummy_cluster["mongoURIWithOptions"]
        del dummy_cluster["mongoURIUpdated"]
        del dummy_cluster["stateName"]
        dummy_cluster["diskSizeGB"] = 60
        dummy_cluster["paused"] = False
        created_cluster = self._api.create_cluster(dummy_cluster.project_id, dummy_cluster.name, dummy_cluster.resource)
        read_cluster = self._api.get_one_cluster("5a141a774e65811a132a8010", dummy_cluster.name)
        #self.assertEqual(dummy_cluster, read_cluster)
        self._api.delete_cluster(dummy_cluster)

    def test_organization(self):
        org = self._api.get_organization()
        self.assertEqual(org["id"], "599eeced9f78f769464d175c")
        self.assertEqual(org["name"], "Open Data at MongoDB")

    def test_projects(self):
        projects = list(self._api.get_project_ids())
        # print(projects)
        self.assertTrue("5f5fb85be8f4302a2bc457f1" in projects)

    def test_authenticated(self):
        api = AtlasAPI()
        with self.assertRaises(AtlasError):
            project = api.get_one_project("5a141a774e65811a132a8010")

        api.authenticate()
        project = api.get_one_project("5a141a774e65811a132a8010")
        self.assertEqual(type(project), type(AtlasProject()))

if __name__ == '__main__':
    unittest.main()
