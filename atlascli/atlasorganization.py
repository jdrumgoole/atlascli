
from typing import List, Dict, Generator

from colorama import Fore

from atlascli.atlasapi import AtlasAPI
from atlascli.atlasproject import AtlasProject
from atlascli.atlascluster import AtlasCluster
from atlascli.atlaskey import AtlasKey

import pprint

from atlascli.atlasresource import AtlasResource

class AtlasClusters:
    #
    # The Atlas API uses IDs for everything but for Cluster operations it uses
    # the name. However this means that names are not guaranteed to be unique. 
    # However it is rare to have a organization with a lot of identical cluster names
    # across its org. We can use this property to simplify the command line
    # by allowing users to just specify the clustername except where it is not unique.
    # We use this class to manage that mapping. 
    # Each cluster name maps to a list of clusters it may be associated with.
    #


    def __init__(self, clusters:List[AtlasCluster]):
        pass
    
class AtlasOrganization(AtlasResource):

    def __init__(self, public_key=None, private_key=None):
 
        api = AtlasAPI(AtlasKey(public_key, private_key))
        super().__init__(api, api.get_organization())
        self._clusters = []
        self._projects = {}
        #pprint.pprint(self._projects)
        self._project_cluster_map = {} 
        for project in [ AtlasProject(self.api, x) for x in self._api.get_projects()]:
            #pprint.pprint(project)
            self._projects[project.id] = project
            clusters = [ AtlasCluster(self._api, project.id, x) for x in self._api.get_clusters(project.id)]
            self._clusters.extend(clusters)
            #pprint.pprint(clusters)
            self._project_cluster_map[project.id] = clusters
        #pprint.pprint(list(self._project_cluster_map.keys()))

    @property
    def api(self):
        return self._api


    def summary(self)->str:
        return f"{Fore.MAGENTA}Organization ID{Fore.RESET}: {self.id} {Fore.MAGENTA}Name{Fore.RESET}: {Fore.LIGHTYELLOW_EX}'{self.name}'"

    def is_project_id(self, id:str)->bool:
        return id in self._projects

    def is_cluster_name(self, cluster_name:str)->bool:
        #print(f"is_cluster_name({cluster_name})")
        #pprint.pprint([x.name for x in self._clusters])
        return any([ x.name == cluster_name for x in self._clusters])


    def is_unique(self, cluster_name:str) -> bool:
        l = self.get_cluster(cluster_name)
        return len(l) == 1

    def get_project_ids(self, cluster_name:str):
        project_ids = []
        for project_id, project in self._projects.items():
            for cluster in self._project_cluster_map[project_id]:
                if cluster.name == cluster_name:
                    project_ids.append(project.id)
        return project_ids


    def __str__(self):
        return f"{pprint.pformat(self._resource)}"
    # def __str__(self):
    #     return f"id:{self.id} name:'{self.name}'"

    def get_projects(self)->Dict[str, AtlasProject]:
        return list(self._projects.values())

    def get_project_id(self, project_name:str):
        for i in self._projects.values():
            if i.name == project_name:
                return i.id
        return None

    def get_project_name(self, project_id:str):
        for i in self._projects.values():
            #pprint.pprint(i.id)
            if i.id == project_id:
                return i.name
        return None
 
    def get_cluster(self, cluster_name:str, project_id=None)->List[AtlasCluster]:
        # 
        # Cluster names are not unique so we might get more than one cluster
        # when we request a cluster.
        #
        clusters = [] 
        for i in self._clusters:
            if i.name == cluster_name:
                if project_id is None:
                    clusters.append(i)
                elif project_id == i.project_id:
                    clusters.append(i)
        return clusters
 
    def get_clusters(self, project_id:str=None)->Generator[AtlasCluster, None, None]:
        for c in self._clusters:
            if project_id is None:
                yield c
            elif project_id == c.project_id:
                yield c


    def pause_cluster(self, project_id:str, cluster_name:str):
        clusters = self.get_clusters()

    def pprint(self):
        print(self.summary())
        for project in self._projects.values():
            print(f"   {project.summary()}")
            for cluster in self._project_cluster_map[project.id]:
                print(f"     {cluster.summary()}")


