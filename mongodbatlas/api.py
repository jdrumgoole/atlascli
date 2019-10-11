"""
MongoDB Atlas Organisation
~~~~~~~~~~~~~~~~~~~~~~~~~~

An organisation is a top level artefact. Users can
create multiple organizations and be members of multiple
organizations. Each organization can have 0 or more
projects (also called groups) and each project can have 0 or
more clusters.

Author:joe@joedrumgoole.com
"""
from functools import lru_cache
from mongodbatlas.apimixin import APIMixin
from mongodbatlas.atlasorganization import AtlasOrganization
from mongodbatlas.atlasproject import AtlasProject
from mongodbatlas.atlascluster import AtlasCluster

from mongodbatlas.atlaskey import AtlasKey


class API(APIMixin):

    def __init__(self, key:AtlasKey=None):
        super().__init__(key)

    def get_organizations(self):
        for org in self.get_resource_by_item("/orgs"):
            yield AtlasOrganization(org)

    def get_this_organizations(self):
        for org in self.get_resource_by_item("/orgs"):
            return AtlasOrganization(org)

    @lru_cache(maxsize=500)
    def get_one_cached_organization(self, organization_id):
        return AtlasOrganization(self.get(f"/orgs/{organization_id}"))

    def get_one_organization(self, org_id):
        return AtlasOrganization(self.atlas_get(f"/orgs/{org_id}"))

    def create_organization(self, name):
        return AtlasOrganization(self.atlas_post(f"/orgs", { "name" : name}))

    def delete_organization(self, name):
        return self.atlas_delete(f"/orgs/{name}")

    #
    # Project Methods
    #

    def create_project(self, org_id, project_name):
        return AtlasProject(self.atlas_post(resource=f"/groups", data={"name": project_name, "orgId": org_id}))

    def delete_project(cls, project_id):
        return cls.atlas_delete(f"/groups/{project_id}")

    def get_projects(self):
        for project in self.get_resource_by_item(f"/groups"):
            yield AtlasProject(project)

    def get_one_project(self, project_id):
        return AtlasProject(self.atlas_get(f"/groups/{project_id}"))

    @lru_cache(maxsize=500)
    def get_one_cached_project(self, project_id):
        return AtlasProject(self.get(f"/groups/{project_id}"))

    def get_project_ids(self):
        for project in self.get_resource_by_item(f"/groups"):
            yield project["id"]

    #
    # Cluster Methods
    #

    @staticmethod
    def cluster_url(project_id, cluster_name):
        return f"/groups/{project_id}/clusters/{cluster_name}"

    def create_cluster(self, project_id, cluster_config):
        return AtlasCluster(self.atlas_post(f"/{project_id}/clusters", cluster_config))

    def get_clusters(self, project_id):
        for cluster in self.get_resource_by_item(f"/groups/{project_id}/clusters"):
            yield AtlasCluster(cluster)

    @lru_cache(maxsize=500)
    def get_one_cached_cluster(self, project_id, cluster_name):
        return self.get(f"/groups/{project_id}/clusters/{cluster_name}")

    def get_one_cluster(self, project_id, cluster_name):
        return AtlasCluster(self.atlas_get(self.cluster_url(project_id, cluster_name)))

    @property
    def paused(self):
        return self._resource["paused"]

    @property
    def running(self):
        return not self._resource["paused"]

    def pause(self, project_id):
        if self.paused:
            return None

        else:
            pause_doc = {"paused": True}
            return self.atlas_patch(f"/groups/{project_id}/clusters/{self.name}", pause_doc)

    def resume(self, project_id):

        if self.paused:
            pause_doc = {"paused": False}
            return self.atlas_patch(f"/groups/{project_id}/clusters/{self.name}", pause_doc)
        else:
            return None









