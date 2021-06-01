import unittest
import pprint

from atlascli.atlasapi import AtlasAPI
from atlascli import AtlasOrganization, AtlasProject


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self._api = AtlasAPI()

    def test_organization(self):
        org = self._api.get_organization()
        self.assertEqual(org["id"], "599eeced9f78f769464d175c")
        self.assertEqual(org["name"], "Open Data at MongoDB")

    def test_projects(self):
        projects = list(self._api.get_project_ids())
        # print(projects)
        self.assertTrue( "5f5fb85be8f4302a2bc457f1" in projects)

if __name__ == '__main__':
    unittest.main()
