import json
import unittest
import logging
import pprint

from atlascli.atlasapi import AtlasAPI
from atlascli.atlascluster import AtlasCluster
from atlascli.errors import AtlasGetError
from atlascli.config import Config
from atlascli.atlaskey import AtlasKey


class TestAPI(unittest.TestCase):

    ORG_ID = "5d97bcac9ccf641309000a18"
    ORG_NAME = "Dummy Organisation"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cfg = Config()
        public_key, private_key = self._cfg.get_keys("Dummy Organisation")
        assert public_key is not None
        assert private_key is not None

        self._api = AtlasAPI()
        self._api.authenticate(AtlasKey(public_key=public_key, private_key=private_key))

    def setUp(self) -> None:
        pass

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

    def test_cluster(self):
        project_name = AtlasAPI.random_name()
        cluster_name = AtlasAPI.random_name()
        project = self._api.create_project(org_id=TestAPI.ORG_ID, project_name=project_name)
        with open("stripped_demodata.json", "r") as input_file:
            cfg = json.load(input_file)
        cluster = self._api.create_cluster(project_id=project.id, name=cluster_name, config=cfg)
        self._api.delete_cluster(cluster)
        while True:
            cluster_names = [x.name for x in self._api.get_clusters(project.id)]
            if cluster_name not in cluster_names:
                break

        self._api.delete_project(project.id)
        while True:
            project_names = [x.name for x in self._api.get_projects()]
            if project.name not in project_names:
                break


if __name__ == '__main__':
    unittest.main()
