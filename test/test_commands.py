import unittest
import sys

from atlascli.main import main


class TestCommands(unittest.TestCase):

    def cmd(self, *args):
        arg_list = list(args)
        print(f"main({arg_list})")
        main(arg_list)

    def setUp(self):
        self._save = sys.stdout
        sys.stdout = open(f"{__file__}.log", "w")

    def tearDown(self):
        sys.stdout = self._save

    def test_main(self):
        self.cmd()
        self.cmd("-h")

    def test_list(self):
        self.cmd("list")

        self.cmd("list", "-c")
        self.cmd("list", "-p")

        self.cmd("list", "-c", "MOT")
        self.cmd("list", "-p", "5a141a774e65811a132a8010")
        self.cmd("list", "-p", "5a141a774e65811a132a8010", "-c")


if __name__ == '__main__':
        unittest.main()

