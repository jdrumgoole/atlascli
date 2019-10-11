import unittest
import pprint

from mongodbatlas.api import API
from mongodbatlas import AtlasOrganization, AtlasProject


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self._api = API()

    def test_organization(self):
        org_list = list(self._api.get_organizations())
        for i in org_list:
            self.assertEqual(i.id, "599eeced9f78f769464d175c")
            self.assertEqual(i.name, "Open Data at MongoDB")

    def test_projects(self):
        projects = list(self._api.get_project_ids())
        print(projects)
        self.assertTrue( "5d9c7e74cf09a246348add09" in projects)

if __name__ == '__main__':
    unittest.main()
