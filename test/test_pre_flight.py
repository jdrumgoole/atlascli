import unittest
from atlascli.commands import Commands
from atlascli.atlasmap import AtlasMap

class TestPreFlight(unittest.TestCase):

    def test_preflight(self):
        map = AtlasMap()
        map.authenticate()
        c = Commands(map)
        with self.assertRaises(SystemExit) as e:
            c.preflight_cluster_arg("xxxxx")

        print(f"raised '{e}'")

        a = c.preflight_cluster_arg("demodata")
        print(a)
if __name__ == '__main__':
    unittest.main()
