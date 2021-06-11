import unittest

import pprint

from atlascli.atlasapi import AtlasAPI
from atlascli import AtlasOrganization


class TestPauseResume(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._org = AtlasOrganization()


    def test_pause(self):
        cluster = self._org.get_cluster("MOT")[0]
        if not cluster.is_paused():
            cluster.pause_cluster()

    def test_resume(self):
        cluster = self._org.get_cluster("MOT")[0]
        if cluster.is_paused(): 
            cluster.resume_cluster()

if __name__ == '__main__':
    unittest.main()
