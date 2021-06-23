import itertools
from typing import Dict, List, Generator

from atlascli.atlasapi import AtlasAPI
from atlascli.atlascluster import AtlasCluster
from atlascli.atlaskey import AtlasKey
from atlascli.atlasorganization import AtlasOrganization
from atlascli.atlasproject import AtlasProject
from atlascli.clusterid import ClusterID


class AtlasMap:
    #
    # Maintain of the complete organization
    #
    # Each org can have multiple projects.
    # Each project can have multiple clusters.
    # Each cluster represents a group of machines/nodes. Clusters may be sharded.
    #

    def __init__(self, org: AtlasOrganization = None, api: AtlasAPI = None, populate: bool = False):

        self._org = org
        self._populate = populate
        self._clusters : List[AtlasCluster] = None
        self._project_map : Dict[str, Dict] = None  # map of all project ids to projects

        self._project_cluster_map: Dict[str, Dict[str, AtlasCluster]] = {}
        # map from project id to a dict of clusters
        # because cluster names are not unique across and organization
        # we have to key each collection of clusters under a specific project id.


        if api:
            self._api = api
        else:
            self._api = AtlasAPI()

        if self._populate:
            self.populate()

    def authenticate(self, k: AtlasKey = None):
        self._api.authenticate(k)

    @property
    def api(self):
        return self._api

    @property
    def projects(self):
        if self._project_map is None:
            self._project_map = {x.id: x for x in self._api.get_projects()}
        return list(self._project_map.values())

    @property
    def clusters(self):
        if self._clusters is None:
            clusters = []
            if len(self._project_cluster_map) == 0:
                self.populate_cluster_map()

            # return list(itertools.chain.from_iterable(self._project_cluster_map.values()))
            for project_id, cluster_dict in self._project_cluster_map.items():
                for cluster_name, cluster in cluster_dict.items():
                    clusters.append(cluster)

            self._clusters = clusters

        return self._clusters

    @property
    def organization(self):
        return self._org

    # def populate(self):
    #     self.populate_clusters()

    @property
    def project_cluster_map(self):
        if len(self._project_cluster_map) == 0:
            self.populate_cluster_map()
        return self._project_cluster_map

    def populate_cluster_map(self):
        new_projects_map = {}
        new_project_cluster_map = {}
        for project in self._api.get_projects():
            new_projects_map[project.id] = project
            new_project_cluster_map[project.id] = {}
            for cluster in self._api.get_clusters(project.id):
                new_project_cluster_map[project.id][cluster.name] = cluster
            assert len(new_projects_map) == len(new_project_cluster_map)

        self._project_cluster_map = new_project_cluster_map
        self._project_map = new_projects_map

    def is_project_id(self, project_id: str) -> bool:
        return project_id in [ x.id for x in self.projects]

    def is_cluster_name(self, cluster_name: str) -> bool:
        # print(f"is_cluster_name({cluster_name})")
        # pprint.pprint([x.name for x in self._clusters])
        return any([x.name == cluster_name for x in self.clusters])

    def is_unique_cluster(self, cluster_name: str) -> bool:
        l = self.get_cluster(cluster_name)
        if len(l) == 1:
            return l[0]
        else:
            return None

    def get_cluster_names(self):
        for i in self.clusters:
            yield i.name

    def get_cluster_project_ids(self, cluster_name: str):
        project_ids = []
        for project_id, cluster_map in self.project_cluster_map.items():
            for name, cluster in cluster_map.items():
                if name == cluster_name:
                    project_ids.append(project_id)
        return project_ids

    def get_project_ids(self) -> List[str]:
        return [ x.id for x in self.projects]

    def get_one_project(self, project_id:str) -> AtlasProject:
        return self._project_map[project_id]

    def get_projects(self) -> Dict[str, AtlasProject]:
        return self._project_map

    def get_project_id(self, project_name: str):
        for i in self.projects:
            #print(i.name)
            if i.name == project_name:
                return i.id
        return None

    def get_project_name(self, project_id: str):
        for i in self.projects:
            if i.id == project_id:
                return i.name
        return None

    def get_cluster(self, cluster_name: str, project_id: object = None) -> List[AtlasCluster]:
        #
        # Cluster names are not unique so we might get more than one cluster
        # when we request a cluster.
        #
        clusters = []
        for i in self.clusters:
            if i.name == cluster_name:
                if project_id is None:
                    clusters.append(i)
                elif project_id == i.project_id:
                    clusters.append(i)
        return clusters

    def get_one_cluster(self, project_id:str, cluster_name:str) -> AtlasCluster:
        clist = self.get_cluster(cluster_name, project_id)
        if len(clist) == 0:
            raise ValueError(f"No such cluster {project_id}:{cluster_name}")
        else:
            assert len(clist) == 1
            return clist[0]

    def get_clusters(self, project_id: str = None) -> Generator[AtlasCluster, None, None]:
        for c in self.clusters:
            if project_id is None:
                yield c
            elif project_id == c.project_id:
                yield c

    def create_cluster(self, project_id:str, cluster_name: str) -> AtlasCluster:
        c = self._api.create_cluster(project_id, cluster_name)
        self._project_cluster_map[project_id]


    def parse_cluster_id(self, cluster_str: str) -> ClusterID:
        cluster_id = ClusterID.parse(cluster_str, throw_exception=True)
        if self.is_project_id(cluster_id.project_id):
            if self.is_cluster_name(cluster_id.name):
                return cluster_id
            else:
                return ValueError(f"{cluster_id.name} is not a valid cluster name in this organization")
        else:
            return ValueError(f"{cluster_id.project_id}is not a valid project id in this organization")

    def pprint(self):
        print(self._org.summary())
        for project in self.projects:
            print(f" Project: {project.pretty_project_id():<40}")
            for v in self.project_cluster_map[project.id].values():
                print(f"  Cluster: {v.summary()}")

