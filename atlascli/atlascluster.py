from __future__ import annotations
import json
import pprint
from typing import Dict, Type, List

from colorama import Fore, Style

from atlascli.atlasresource import AtlasResource


class AtlasCluster(AtlasResource):

    @classmethod
    def default_single_region_cluster(cls):
        return {
            # "name" : "DataStore",
            "diskSizeGB": 100,
            "numShards": 1,
            "providerSettings": {
                "providerName": "AWS",
                "diskIOPS": 300,
                "instanceSizeName": "M40",
                "regionName": "US_EAST_1"
            },
            "replicationFactor": 3,
            "autoScaling": {"diskGBEnabled": True},
        }

    def __init__(self, project_id: str, name: str = None, cluster_config: Dict = None):

        super().__init__(cluster_config)
        self._project_id = project_id
        self.name = name

    @staticmethod
    def strip(d: Dict, keys : List[str]):
        for k in keys:
            if k in d:
                del d[k]
        return d

    @staticmethod
    def strip_cluster_dict(cluster: Dict) -> Dict:
        #
        # Strip out keys that cannot be used to create a cluster from an existing
        # configuration
        #
        d = AtlasCluster.strip(cluster, ["connectionStrings",
                                         "replicationSpecs",
                                         "mongoURI",
                                         "mongoURIWithOptions",
                                         "mongoURIUpdated",
                                         "paused",
                                         "stateName"])

        return d

    @staticmethod
    def strip_cluster(cluster: AtlasCluster) -> AtlasCluster:
        return AtlasCluster(cluster.project_id,
                            cluster.name,
                            AtlasCluster.strip_cluster_dict(cluster.resource))

    @property
    def cluster_id(self):
        return self.id

    @property
    def project_id(self):
        return self._project_id

    def is_paused(self):
        return self.resource["paused"]

    def __str__(self):
        return f"{pprint.pformat(self.resource)}"

    def status(self) -> str:
        if self.resource["stateName"] == "REPAIRING":
            if self.is_paused():
                return f"{Fore.LIGHTRED_EX}Pausing...{Fore.RESET}"
            else:
                return f"{Fore.LIGHTRED_EX}Resuming...{Fore.RESET}"
        elif self.resource["stateName"] == "CREATING":
            return f"{Fore.LIGHTRED_EX}Creating...{Fore.RESET}"
        elif self.resource["stateName"] == "DELETING":
            return f"{Fore.LIGHTRED_EX}Deleting...{Fore.RESET}"
        elif self.resource["stateName"] == "IDLE":
            if self.is_paused():
                return f"{Fore.LIGHTBLUE_EX}Paused{Fore.RESET}"
            else:
                return f"{Fore.RED}running{Fore.RESET}"

    def summary(self):
        return f"{self.pretty_id_name():70} state: {self.status():20}"
