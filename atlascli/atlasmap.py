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

        self._clusters = []
        self._projects = {}
        # pprint.pprint(self._projects)
        self._project_cluster_map = {}

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
    def clusters(self):
        if self._clusters:
            return self._clusters
        else:
            return self.populate_clusters()

    @property
    def organization(self):
        return self._org

    def populate(self):
        self.populate_projects()
        self.populate_clusters()

    @property
    def project_cluster_map(self):
        if self._project_cluster_map:
            return self._project_cluster_map
        else:
            self.populate_clusters()
            return self._project_cluster_map

    def populate_projects(self):
        new_projects = {}
        for project in self._api.get_projects():
            new_projects[project.id] = project
        self._projects = new_projects
        return self._projects

    def populate_clusters(self):
        new_clusters = []
        new_project_cluster_map = {}
        for project in self.projects.values():
            clusters = list(self._api.get_clusters(project.id))
            new_clusters.extend(clusters)
            new_project_cluster_map[project.id] = clusters

        self._clusters = new_clusters
        self._project_cluster_map = new_project_cluster_map

        return self._clusters

    def is_project_id(self, project_id: str) -> bool:
        return project_id in self.projects

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
        for project_id, project in self.projects.items():
            for cluster in self.project_cluster_map[project_id]:
                if cluster.name == cluster_name:
                    project_ids.append(project.id)
        return project_ids

    def get_project_ids(self) -> List[str]:
        return list(self.projects.keys())

    def get_one_project(self, project_id:str) -> AtlasProject:
        return self.projects[project_id]

    def get_projects(self) -> Dict[str, AtlasProject]:
        return list(self.projects.values())

    def get_project_id(self, project_name: str):
        for i in self.projects.values():
            if i.name == project_name:
                return i.id
        return None

    def get_project_name(self, project_id: str):
        for i in self.projects.values():
            # pprint.pprint(i.id)
            if i.id == project_id:
                return i.name
        return None

    @property
    def projects(self):
        if self._projects:
            return self._projects
        else:
            return self.populate_projects()

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
        for project in self.projects.values():
            print(f"  Project: {project.pretty_id_name():<40}")
            for cluster in self.project_cluster_map[project.id]:
                print(f"     Cluster: {cluster.summary()}")

