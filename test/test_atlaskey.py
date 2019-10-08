import unittest
import os

from mongodbatlas.atlaskey import AtlasKey, AtlasEnv
from mongodbatlas.errors import AtlasEnvironmentError


class MyTestCase(unittest.TestCase):

    def test_atlaskey(self):

        key = AtlasKey(private_key="AAAAAAAAAA", public_key="BBBBBBBBBBB")
        self.assertEqual(str(key), "AtlasKey(public_key='xxxxxxxBBBB', private_key='xxxxxxAAAA')")

    def test_env(self):
        os.environ[AtlasEnv.ATLAS_PUBLIC_KEY.value] = "123456789"
        os.environ[AtlasEnv.ATLAS_PRIVATE_KEY.value] = "987654321"
        key = AtlasKey.get_from_env()
        self.assertEqual(key, "AtlasKey(public_key='xxxxx1234', private_key='xxxxx9876')")
        del os.environ[AtlasEnv.ATLAS_PUBLIC_KEY.value]
        del os.environ[AtlasEnv.ATLAS_PRIVATE_KEY.value]

    def test_no_env(self):
        with self.assertRaises(AtlasEnvironmentError):
            _=AtlasKey.get_from_env()

if __name__ == '__main__':
    unittest.main()
