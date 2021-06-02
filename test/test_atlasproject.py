import unittest

from atlascli.atlasapi import AtlasAPI
from atlascli.atlasproject import AtlasProject
from atlascli.errors import AtlasGetError


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self._api = AtlasAPI()

    def test_create_delete(self):

        name = AtlasAPI.random_name()
        project = self._api.create_project("599eeced9f78f769464d175c", name)
        self.assertEqual(name, project["name"])
        self._api.delete_project(project["id"])
        with self.assertRaises(AtlasGetError) as e:
            self._api.get_one_project(project["id"])


if __name__ == '__main__':
    unittest.main()
