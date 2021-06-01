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
from typing import Generator, List, Dict

from atlascli.atlasrequests import AtlasRequests
from atlascli.atlaskey import AtlasKey


class AtlasAPI:

    def __init__(self, atlas_key:AtlasKey=None):
        self._atlas_requests = AtlasRequests(atlas_key)

    @property
    def api_key(self):
        return self._atlas_requests.api_key

    def get_organization(self) -> Dict:
        """
        https://docs.atlas.mongodb.com/reference/api/organization-get-all/
        GET /orgs
        curl --include --user "{PUBLIC-KEY}:{PRIVATE-KEY}" --digest \
        --header "Accept: application/json" \
        --header "Content-Type: application/json" \
        "https://cloud.mongodb.com/api/atlas/v1.0/orgs"
        :return: list of AtlasOrganisations as a generator
        """
        for org in self._atlas_requests.get_resource_by_item("/orgs"):
            return org

    def get_this_organization(self) -> dict:
        """
        Get the organization. As there is only one organization associated
        with a programmatic key this returns that organization.

        :return: AtlasOrganization
        """
        for org in self._atlas_requests.get_resource_by_item("/orgs"):
            return org

    @lru_cache(maxsize=500)
    def get_one_cached_organization(self, org_id:str)->Dict:
        return self._atlas_requests.get(f"/orgs/{org_id}")

    def get_one_organization(self, org_id:str)->dict:
        return self._atlas_requests.atlas_get(f"/orgs/{org_id}")

    def create_organization(self, name:str)->dict:
        return self._atlas_requests.atlas_post(f"/orgs", { "name" : name})

    def delete_organization(self, name):
        return self._atlas_requests.delete(f"/orgs/{name}")

    #
    # Project Methods
    #

    def create_project(self, org_id, project_name)->Dict:
        """
        https://docs.atlas.mongodb.com/reference/api/project-create-one/
        POST /api/atlas/v1.0/groups
        curl -u "{PUBLIC-KEY}:{PRIVATE-KEY}" --digest -H "Content-Type: application/json" -X POST "https://cloud.mongodb.com/api/atlas/v1.0/groups" --data '{ "name" : "ProjectFoobar", "orgId" : "5a0a1e7e0f2912c554080adc" }'
        :param org_id:
        :param project_name:
        :return: project doc
        """
        return self._atlas_requests.atlas_post(resource=f"/groups", data={"name": project_name, "orgId": org_id})

    def delete_project(self, project_id)->Dict:
        """
        https://docs.atlas.mongodb.com/reference/api/project-delete-one/
        DELETE /api/atlas/v1.0/groups/{GROUP-ID}
        curl -X DELETE --digest -u "{PUBLIC-KEY}:{PRIVATE-KEY}" "https://cloud.mongodb.com/api/atlas/v1.0/groups/6c819f1b87d9d6037bc2cdb1"
        :param project_id:
        :return: deleted project doc
        """
        return self._atlas_requests.atlas_delete(f"/groups/{project_id}")

    def get_projects(self)->Generator[dict, None, None]:
        for project in self._atlas_requests.get_resource_by_item(f"/groups"):
            yield project

    def get_one_project(self, project_id)->Dict:
        """
        https://docs.atlas.mongodb.com/reference/api/project-get-one/
        GET /api/atlas/v1.0/groups/{GROUP-ID}
        curl -i -u "{PUBLIC-KEY}:{PRIVATE-KEY}" --digest "https://cloud.mongodb.com/api/atlas/v1.0/groups/5a0a1e7e0f2912c554080ae6"
        :param project_id:
        :return:
        """
        return self._atlas_requests.atlas_get(f"/groups/{project_id}")

    @lru_cache(maxsize=500)
    def get_one_cached_project(self, project_id)->dict:
        return self._atlas_requests.atlas_get(f"/groups/{project_id}")

    def get_project_ids(self)->Generator[str, None, None]:
        for project in self._atlas_requests.get_resource_by_item(f"/groups"):
            yield project["id"]

    #
    # Cluster Methods
    #

    @staticmethod
    def cluster_url(project_id, cluster_name):
        return f"/groups/{project_id}/clusters/{cluster_name}"

    def create_cluster(self, project_id, cluster_config):
        return self._atlas_requests.atlas_post(f"/groups/{project_id}/clusters", cluster_config)

    def get_clusters(self, project_id)->Generator[str, None, None]:
        for cluster in self._atlas_requests.get_resource_by_item(f"/groups/{project_id}/clusters"):
            yield cluster

    def delete_cluster(self, project_id, cluster_name)->dict:
        """
        DELETE /api/atlas/v1.0/groups/{GROUP-ID}/clusters/{CLUSTER-NAME}
        https://docs.atlas.mongodb.com/reference/api/clusters-delete-one/
        """
        return self._atlas_requests.atlas_delete(f"/groups/{project_id}/clusters/{cluster_name}")

    def modify_cluster(self, project_id, cluster_name, modifications):
        """
        PATCH /groups/{GROUP-ID}/clusters/{CLUSTER-NAME}
        https://docs.atlas.mongodb.com/reference/api/clusters-modify-one/
        :param project_id:
        :param cluster_name:
        :param modifications:  A dict defining the fields to be changed
        :return: a Change doc reflecting the updated cluster
        """

        return self._atlas_requests.atlas_patch(f"/groups/{project_id}/clusters/{cluster_name}", data=modifications)

    @lru_cache(maxsize=500)
    def get_one_cached_cluster(self, project_id, cluster_name):
        return self._atlas_requests.atlas_get(f"/groups/{project_id}/clusters/{cluster_name}")

    def get_one_cluster(self, project_id, cluster_name)->dict:
        return self._atlas_requests.atlas_get(self.cluster_url(project_id, cluster_name))

    def pause(self, project_id, cluster_name):
        pause_doc = {"paused": True}
        return self._atlas_requests.atlas_patch(f"/groups/{project_id}/clusters/{cluster_name}", pause_doc)

    def resume(self, project_id, cluster_name):
        pause_doc = {"paused": False}
        return self._atlas_requests.atlas_patch(f"/groups/{project_id}/clusters/{cluster_name}", pause_doc)


    # def pprint(self, atlas_object, fmt=OutputFormat.SUMMARY):
    #     if atlas_object is AtlasOrganization:
    #         print("{0:<8}".format(self), end="")
    #         print(atlas_object)
    #         projects = self._atlas_api.get_projects()
    #         for project in projects:
    #             print("{0:<8}".format("Project"), end="")
    #             print(project)
    #             clusters = self._atlas_api.get_clusters(project.id)
    #             for cluster in clusters:
    #                 print("{0:<8}".format("Cluster"), end="")
    #                 print(cluster)

    def __repr__(self):
        return f"AtlasAPI(api_key={self._atlas_requests})"





