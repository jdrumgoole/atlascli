import unittest

from mongodbatlas.api import API, AtlasOrganization, AtlasProject
from mongodbatlas.errors import AtlasGetError
class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self._api = API()
        self._org= self._api.get_this_organization()

    def test_create_delete(self):

        name = AtlasProject.random_name()
        project = self._api.create_project(self._org.id, name)
        self.assertEqual(name, project.name)
        self._api.delete_project(project.id)
        with self.assertRaises(AtlasGetError) as e:
            self._api.get_one_project(project.id)


if __name__ == '__main__':
    unittest.main()
