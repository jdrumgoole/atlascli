import unittest
from mongodbatlas.api import AtlasOrganization
class MyTestCase(unittest.TestCase):

    def test_organization(self):
        for i in AtlasOrganization().get_organizations():
            self.assertTrue( type(i) == AtlasOrganization)

if __name__ == '__main__':
    unittest.main()
