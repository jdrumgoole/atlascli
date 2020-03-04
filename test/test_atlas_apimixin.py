import unittest
import pprint

from mongodbatlas.atlasrequests import AtlasRequests
from mongodbatlas.atlaskey import AtlasKey
from mongodbatlas import AtlasProject

import requests

class Test_APIMixin(unittest.TestCase):


    def setUp(self):
        key = AtlasKey.get_from_env()
        self._api=AtlasRequests(api_key=key, debug=1)

    def tearDown(self):
        pass

    def test_get(self):
        r = self._api.get("https://jsonplaceholder.typicode.com/posts/1")
        org=self._api.atlas_get("/orgs/599eeced9f78f769464d175c")
        #pprint.pprint(org)
        self.assertEqual(org["name"], "Open Data at MongoDB")

    def test_get_projects(self):
        resource="/groups"
        for project in AtlasProject().get_resource_by_item(resource):
            self.assertTrue(type(project) == dict)

    def test_post(self):
        pass
