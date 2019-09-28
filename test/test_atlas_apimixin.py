import unittest
from atlasapi.apimixin import APIMixin
from atlasapi.atlaskey import AtlasKey

import requests

class Test_APIMixin(unittest.TestCase):


    def setUp(self):
        key = AtlasKey.get_from_env()
        self._api=APIMixin(api_key=key, debug=1)

    def tearDown(self):
        pass

    def test_get(self):
        r = self._api.get("https://jsonplaceholder.typicode.com/posts/1")
        self.assertEqual(r.status_code, requests.codes.ok)
        #r.raise_for_status()


    def test_post(self):
        # r = self._api.post("https://jsonplaceholder.typicode.com/posts", {'handle1' : '@jdrumgoole'})
        # self.assertEqual(r.status_code, 201)

        self._api.atlas_post("/orgs", {"name": "Drumgoole Test Organization"})

    # def test_atlas_get(self):
    #     r = self._api.atlas_get("/orgs/599eeced9f78f769464d175c")
    #     self.assertEqual(r.status_code, 200)
    #     #r.raise_for_status()
