import unittest
import os

from atlascli.config import Config


class TestConfig(unittest.TestCase):

    def test_load_config(self):
        org="tester"
        cfg = Config(filename="atlascli.cfg.test")
        cfg.save_keys("public_xxx", "private_xxx", org=org)
        new_cfg = Config(filename="atlascli.cfg.test")
        self.assertEqual(cfg.get_keys(org=org), new_cfg.get_keys(org=org))

        new_cfg.save_keys("public_yyy", "private_yyy", org="new org")

        cfg = Config(filename="atlascli.cfg.test")

        self.assertEqual(cfg.get_keys(org=org), new_cfg.get_keys(org=org))
        self.assertEqual(cfg.get_keys(org="new org"), new_cfg.get_keys(org="new org"))
        os.unlink("atlascli.cfg.test")

        #print(cfg)

if __name__ == '__main__':
    unittest.main()
