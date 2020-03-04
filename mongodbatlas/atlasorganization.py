import pprint

from mongodbatlas.atlasresource import AtlasResource


class AtlasOrganization(AtlasResource):

    def __init__(self, org=None):
        super().__init__(org)
        self._projects = {}

        self._project_cluster_map = {}

    def add_projects(self, projects):
        for project in projects:
            self._projects[project.id] = project

    def add_clusters(self, project_id, clusters):
        self._project_cluster_map[project_id] = {}
        for cluster in clusters:
            self._project_cluster_map[ project_id][cluster.id] = cluster
        return self._project_cluster_map[ project_id]

    def __str__(self):
        return f"Organization:\n{pprint.pformat(self._resource)}"
    # def __str__(self):
    #     return f"id:{self.id} name:'{self.name}'"

    def pprint(self):
        print(self)
        for project in self._projects.values():
            print(f"   {project}")
            for cluster in self._project_cluster_map[project.id].values():
                print(f"      {cluster}")

