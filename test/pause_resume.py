import unittest

import pprint

from mongodbatlas.opcapi import OPCAPI
from mongodbatlas import AtlasCluster


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self._api = OPCAPI()

    def test_pause(self):
        for project in self._api.get_projects():
            for cluster in self._api.get_clusters(project.id):
                print(f"State: {cluster.summary()}")
                result = cluster.pause(project.id)
                if result is None:
                    print(f"{cluster.id}:{cluster.name} was already paused")
                else:
                    print(f"Pausing {cluster.id}:{cluster.name}")

    def test_resume(self):
        for project in self._api.get_projects():
            for cluster in self._api.get_clusters(project.id):
                print(f"State: {cluster.summary_string()}")
                result = cluster.resume(project.id)
                if result is None:
                    print(f"{cluster.id}:{cluster.name} was already running")
                else:
                    print(f"Resuming {cluster.id}:{cluster.name}")

if __name__ == '__main__':
    unittest.main()
