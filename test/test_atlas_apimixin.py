import unittest
import pprint

from atlascli.atlasapi import AtlasAPI


class TestAPIMixin(unittest.TestCase):

    def setUp(self):
        self._api= AtlasAPI()
        self._api.authenticate()

    def tearDown(self):
        pass

    def test_get(self):
        r = self._api.get("https://httpbin.org/get")
        #pprint.pprint(r)
        self.assertEqual(r["args"], {'itemsPerPage': '100', 'pageNum': '1'})
        org=self._api.atlas_get("/orgs/599eeced9f78f769464d175c")
        #pprint.pprint(org)
        self.assertEqual(org["name"], "Open Data at MongoDB")

    def test_post(self):
        r = self._api.post("https://httpbin.org/post", {"Hello":"World"})
        self.assertEqual(r["data"], '{"Hello": "World"}')

    def test_patch(self):
        r = self._api.patch("https://httpbin.org/patch", {"Hello":"World"})
        self.assertEqual(r["data"], '{"Hello": "World"}')

    def test_delete(self):
        r = self._api.delete("https://httpbin.org/delete")
        self.assertEqual(r["data"], '')
        
if __name__ == '__main__':
    unittest.main()