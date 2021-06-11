import unittest
import os

from atlascli.atlaskey import AtlasKey, AtlasEnv
from atlascli.errors import AtlasEnvironmentError


class TestAtlasKey(unittest.TestCase):

    def setUp(self):
        self._public = os.environ[AtlasEnv.ATLAS_PUBLIC_KEY.value]
        self._private = os.environ[AtlasEnv.ATLAS_PRIVATE_KEY.value]

    def tearDown(self):
        os.environ[AtlasEnv.ATLAS_PUBLIC_KEY.value] = self._public
        os.environ[AtlasEnv.ATLAS_PRIVATE_KEY.value] = self._private

    def test_atlaskey(self):
        os.environ[AtlasEnv.ATLAS_PUBLIC_KEY.value] = "Public Key"
        os.environ[AtlasEnv.ATLAS_PRIVATE_KEY.value] = "Private Key"
        key = AtlasKey()
        self.assertEqual( key._private_key, "Private Key")
        self.assertEqual( key._public_key, "Public Key")
        key = AtlasKey(private_key="AAAAAAAAAA", public_key="BBBBBBBBBBB")
        self.assertEqual(str(key), "AtlasKey(public_key='xxxxxxxBBBB', private_key='xxxxxxAAAA')")

    def test_env(self):
        os.environ[AtlasEnv.ATLAS_PUBLIC_KEY.value] = "123456789"
        os.environ[AtlasEnv.ATLAS_PRIVATE_KEY.value] = "987654321"
        key = AtlasKey.get_from_env()
        self.assertEqual(str(key), "AtlasKey(public_key='xxxxx1234', private_key='xxxxx9876')")
        del os.environ[AtlasEnv.ATLAS_PUBLIC_KEY.value]
        del os.environ[AtlasEnv.ATLAS_PRIVATE_KEY.value]

    def test_no_env(self):
        del os.environ[AtlasEnv.ATLAS_PUBLIC_KEY.value]
        del os.environ[AtlasEnv.ATLAS_PRIVATE_KEY.value]
        with self.assertRaises(AtlasEnvironmentError):
            _=AtlasKey.get_from_env()

        with self.assertRaises(AtlasEnvironmentError):
            _=AtlasKey()

if __name__ == '__main__':
    unittest.main()
