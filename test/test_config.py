import shutil
import unittest
import os

from atlascli.atlasapi import AtlasAPI
from atlascli.config import Config


class TestConfig(unittest.TestCase):

    def setUp(self):
        if Config.PUBLIC_KEY_ENV in os.environ:
            del os.environ[Config.PUBLIC_KEY_ENV]
        if Config.PRIVATE_KEY_ENV in os.environ:
            del os.environ[Config.PRIVATE_KEY_ENV]

    def test_config_filename(self):
        cfg = Config()
        self.assertEqual(cfg.filename, cfg.default_config_filename)
        cfg.save_config()
        os.unlink(cfg.filename)
        cfg = Config(filename="test.cfg")
        self.assertEqual(cfg.filename, "test.cfg")
        cfg.save_config()
        os.unlink("test.cfg")

    def test_load_config(self):
        org="tester"
        cfg = Config()
        cfg.load(private_key=None, public_key=None, filename="atlascli.cfg.test")
        self.assertTrue(cfg.filename == "atlascli.cfg.test")
        cfg.save_config_file_keys("public_xxx", "private_xxx", org=org)
        new_cfg = Config(filename="atlascli.cfg.test")
        self.assertEqual(cfg.get_config_file_keys(org=org), new_cfg.get_config_file_keys(org=org))

        new_cfg.save_config_file_keys("public_yyy", "private_yyy", org="new org")

        cfg = Config()
        cfg.load(private_key=None, public_key=None, filename="atlascli.cfg.test")
        self.assertEqual(cfg.get_config_file_keys(org=org), new_cfg.get_config_file_keys(org=org))
        self.assertEqual(cfg.get_config_file_keys(org="new org"), new_cfg.get_config_file_keys(org="new org"))
        os.unlink("atlascli.cfg.test")

        #print(cfg)

    def test_command_line(self):
        os.environ[Config.PUBLIC_KEY_ENV] = "PUB"
        os.environ[Config.PRIVATE_KEY_ENV] = "PRI"

        cfg = Config()
        cfg.load_from_args(public_key="boojum", private_key="taco")
        self.assertEqual(cfg.get_public_key(), "boojum")
        self.assertEqual(cfg.get_private_key(), "taco")

    def test_env(self):
        os.environ[Config.PUBLIC_KEY_ENV] = "PUB"
        os.environ[Config.PRIVATE_KEY_ENV] = "PRI"
        cfg = Config()
        cfg.load_from_env()
        self.assertEqual(cfg.get_public_key(), "PUB")
        self.assertEqual(cfg.get_private_key(), "PRI")

        cfg = Config()
        cfg.load_from_args(public_key="boojum", private_key="taco")
        self.assertEqual(cfg.get_public_key(), "boojum")
        self.assertEqual(cfg.get_private_key(), "taco")

        cfg = Config()
        cfg.load_from_file(input_file="test_atlascli.cfg")
        self.assertEqual(cfg.get_public_key(), "bogus")
        self.assertEqual(cfg.get_private_key(), "20d81ed9-f22c-47d4-a97b-FFFFFFFFFFFF")

    def test_cfg(self):
        cfg = Config()
        cfg.load_from_file(input_file="test_atlascli.cfg")
        self.assertEqual(cfg.get_public_key(), "bogus")
        self.assertEqual(cfg.get_private_key(), "20d81ed9-f22c-47d4-a97b-FFFFFFFFFFFF")

        shutil.copyfile("test_atlascli.cfg", "atlascli.cfg")
        cfg = Config()
        cfg.load_from_file()
        self.assertEqual(cfg.get_public_key(), "bogus")
        self.assertEqual(cfg.get_private_key(), "20d81ed9-f22c-47d4-a97b-FFFFFFFFFFFF")
        self.assertEqual(cfg.get_public_key(org="Open Data at MongoDB"), "Zombie")
        os.unlink("atlascli.cfg")

    def test_bad_cfg_file(self):
        with self.assertRaises(ValueError):
            _ = Config().load_from_file(AtlasAPI.random_name())

    def test_key(self):
        org = "tester"
        cfg = Config(filename="atlascli.cfg.test")
        with self.assertRaises(ValueError):
            cfg.get_public_key("dumbo")

        with self.assertRaises(ValueError):
            cfg.get_private_key("dumbo")

        with self.assertRaises(ValueError):
           _,_ = cfg.get_config_file_keys("wrong org")

    def test_org(self):
        org = "Open Data at MongoDB"
        cfg = Config(default_org=org)
        cfg.load_from_file(input_file="test_atlascli.cfg")
        self.assertTrue(cfg.get_public_key(org).startswith("Zo"))
        public_key, private_key = cfg.get_config_file_keys(org)
        self.assertTrue(public_key.startswith("Zo"))
        self.assertTrue(private_key.startswith("9f3"))


if __name__ == '__main__':
    unittest.main()
