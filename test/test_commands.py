import unittest
import sys

from atlascli.atlasapi import AtlasAPI
from atlascli.main import main
from atlascli.atlasmap import AtlasMap

class TestCommands(unittest.TestCase):

    def cmd(self, *args):
        map = AtlasMap()
        arg_list = list(args)
        print(f"main({arg_list})")
        main(arg_list)

    def setUp(self):
        self._save = sys.stdout
        sys.stdout = open(f"{__file__}.log", "w")

    def tearDown(self):
        sys.stdout.close()
        sys.stdout = self._save

    def test_main(self):
        self.cmd()
        #self.cmd("-h")

    def test_list(self):
        self.cmd("list")

        self.cmd("list", "-c")
        self.cmd("list", "-p")

        self.cmd("list", "-c", "MOT")
        self.cmd("list", "-p", "5a141a774e65811a132a8010")
        self.cmd("list", "-p", "5a141a774e65811a132a8010", "-c")

    def test_create_project(self):
        name = AtlasAPI.random_name()
        self.cmd("create", "-p", name)
        self
    def test_create(self):
        # Assume dummy organization has been configured in atlascli.cfg
        #
        self.cmd("create", "-p", "testcluster")


if __name__ == '__main__':
        unittest.main()

