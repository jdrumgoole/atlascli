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
import string
from functools import lru_cache
import random
from typing import Generator, List, Dict
import logging
import pprint

import requests
from requests.auth import HTTPDigestAuth

from atlascli.atlaskey import AtlasKey
from atlascli.errors import AtlasInitialisationError, AtlasGetError, AtlasPostError


class AtlasAPI:

    SITE_URL = "https://cloud.mongodb.com"
    API_URL = f"/api/atlas/v1.0"
    ATLAS_BASE_URL = f"{SITE_URL}{API_URL}"

    ATLAS_HEADERS = {"Accept"       : "application/json",
                     "Content-Type" : "application/json"}

    def __init__(self, key : AtlasKey = None, page_size: int = 100):
        self._api_key: AtlasKey = key
        self._auth = None
        self._log = logging.getLogger(__name__)
        self._page_size = page_size

        if self._page_size < 1 or self._page_size > 500 :
            raise AtlasInitialisationError("'page_size' must be between 1 and 500")

        if not self._api_key:
            self._api_key = AtlasKey.get_from_env()

        # print(self._username)
        # print(self._api_key)
        self._auth = HTTPDigestAuth(self._api_key.public_key, self._api_key.private_key)

    @property
    def api_key(self):
        return self._atlas_requests.api_key

    def set_logging_level(self, level):
        self._log.setLevel(level)

    @staticmethod
    def random_name():
        return "ATLASCLI-"+''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def post(self, resource, data):
        self._log.debug(f"post({resource}, {data})")

        try:
            #print(f"requests.post(url={resource}, data={data}, headers={self.ATLAS_HEADERS}, auth={self._auth})")
            #print("printing data")
            #pprint.pprint(data)
            r = requests.post(url=resource,
                              json=data,
                              #json=json.dumps(data),
                              headers=self.ATLAS_HEADERS,
                              auth=self._auth)
            #print(r.url)
            r.raise_for_status()

        except requests.exceptions.HTTPError as e:
            error = pprint.pformat(r.json())
            raise AtlasPostError(error)
        return r.json()

    def get(self, resource, headers=None, page_num=1, items_per_page=100):
        self._log.debug(f"get({resource})")
        # Need to use the raw URL when getting linked data

        assert self._api_key is not None
        assert self._api_key != ""

        args =""
        if "itemsPerPage" not in resource:
            args=args+f"?itemsPerPage={items_per_page}"

        if "pageNum" not in resource:
            if len(args) > 0 :
                args = args + "&"
            args=args+f"pageNum={page_num}"

        resource = resource + args

        try:
            r = requests.get(resource,
                             headers=headers,
                             auth=self._auth)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error = pprint.pformat(r.json())
            raise AtlasGetError(error)
        return r.json()

    def atlas_post(self, resource, data):
        return self.post(resource=f"{self.ATLAS_BASE_URL}{resource}", data=data)

    def atlas_get(self,resource=None, page_num=1, items_per_page=100):
        if resource is None:
            resource = ""
        return self.get(f"{self.ATLAS_BASE_URL}{resource}", items_per_page=items_per_page, page_num=page_num)

    def atlas_patch(self, resource, data):
        self._log.debug(f"atlas_patch({resource}, {data})")
        return self.patch(f"{self.ATLAS_BASE_URL}{resource}", data)

    def atlas_delete(self, resource):
        self._log.debug(f"atlas_delete({resource})")
        return self.delete(f"{self.ATLAS_BASE_URL}{resource}")

    def patch(self, resource, patch_doc):
        try:
            p = requests.patch(f"{resource}",
                               json=patch_doc,
                               headers=self.ATLAS_HEADERS,
                               auth=self._auth
                               )
            p.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error = pprint.pformat(p.json())
            raise AtlasPatchError(error)
        return p.json()

    def delete(self, resource):
        self._log.debug(f"delete({resource})")
        try:
            d = requests.delete(f"{resource}", headers=self.ATLAS_HEADERS, auth=self._auth)
            d.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise AtlasDeleteError(e, d.json()["detail"])

        return d.json()

    def get_resource_by_item(self, resource):

        self._log.debug(f"get_resource_by_item({resource})")

        doc = self.atlas_get(resource)
        yield from self._get_results(doc)
        links = doc['links']
        last_link = links[-1]

        while "rel" in last_link and "next" == last_link["rel"]:
            doc = self.get(last_link["href"])
            yield from self._get_results(doc)
            links = doc['links']
            last_link = links[-1]

    def get_resource_by_page(self, resource):
        """
        return each array of resources as a single
        :param resource:
        :return:
        """
        self._log.debug(f"get_resource_by_page({resource})")
        results = None
        next_link = None

        doc = self.atlas_get(resource)

        if 'results' in doc:
            results = doc["results"]
        else:
            raise AtlasGetError(f"No 'results' field in '{doc}'")

        links = doc['links']
        last_link = links[-1]
        # print(links)
        # print(last_link)
        if "rel" in last_link and "next" == last_link["rel"]:
            next_link = last_link["href"]
        else:
            next_link = None

        return results, next_link

    def _get_results(self, doc):
        if 'results' in doc:
            for i in doc["results"]:
                yield i
        else:
            raise AtlasGetError(f"No 'results' field in '{doc}'")

    def get_ids(self, field):
        for i in self.get_resource_by_item(f"/{field}"):
            yield i["id"]

    def get_names(self, field):
        for i in self.get_resource_by_item(f"/{field}"):
            yield i["name"]

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
        for org in self.get_resource_by_item("/orgs"):
            return org

    def get_this_organization(self) -> dict:
        """
        Get the organization. As there is only one organization associated
        with a programmatic key this returns that organization.

        :return: AtlasOrganization
        """
        for org in self.get_resource_by_item("/orgs"):
            return org

    @lru_cache(maxsize=500)
    def get_one_cached_organization(self, org_id:str)->Dict:
        return self.get(f"/orgs/{org_id}")

    def get_one_organization(self, org_id:str)->dict:
        return self.atlas_get(f"/orgs/{org_id}")

    def create_organization(self, name:str)->dict:
        return self.atlas_post(f"/orgs", { "name" : name})

    def delete_organization(self, name):
        return self.delete(f"/orgs/{name}")

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
        return self.atlas_post(resource=f"/groups", data={"name": project_name, "orgId": org_id})

    def delete_project(self, project_id)->Dict:
        """
        https://docs.atlas.mongodb.com/reference/api/project-delete-one/
        DELETE /api/atlas/v1.0/groups/{GROUP-ID}
        curl -X DELETE --digest -u "{PUBLIC-KEY}:{PRIVATE-KEY}" "https://cloud.mongodb.com/api/atlas/v1.0/groups/6c819f1b87d9d6037bc2cdb1"
        :param project_id:
        :return: deleted project doc
        """
        return self.atlas_delete(f"/groups/{project_id}")

    def get_projects(self)->Generator[dict, None, None]:
        for project in self.get_resource_by_item(f"/groups"):
            yield project

    def get_one_project(self, project_id)->Dict:
        """
        https://docs.atlas.mongodb.com/reference/api/project-get-one/
        GET /api/atlas/v1.0/groups/{GROUP-ID}
        curl -i -u "{PUBLIC-KEY}:{PRIVATE-KEY}" --digest "https://cloud.mongodb.com/api/atlas/v1.0/groups/5a0a1e7e0f2912c554080ae6"
        :param project_id:
        :return:
        """
        return self.atlas_get(f"/groups/{project_id}")

    @lru_cache(maxsize=500)
    def get_one_cached_project(self, project_id)->dict:
        return self.atlas_get(f"/groups/{project_id}")

    def get_project_ids(self)->Generator[str, None, None]:
        for project in self.get_resource_by_item(f"/groups"):
            yield project["id"]

    #
    # Cluster Methods
    #

    @staticmethod
    def cluster_url(project_id, cluster_name):
        return f"/groups/{project_id}/clusters/{cluster_name}"

    def create_cluster(self, project_id:str, cluster_config:Dict):
        return self.atlas_post(f"/groups/{project_id}/clusters", cluster_config)

    def get_clusters(self, project_id)->Generator[str, None, None]:
        for cluster in self.get_resource_by_item(f"/groups/{project_id}/clusters"):
            yield cluster

    def delete_cluster(self, project_id, cluster_name)->dict:
        """
        DELETE /api/atlas/v1.0/groups/{GROUP-ID}/clusters/{CLUSTER-NAME}
        https://docs.atlas.mongodb.com/reference/api/clusters-delete-one/
        """
        return self.atlas_delete(f"/groups/{project_id}/clusters/{cluster_name}")

    def modify_cluster(self, project_id, cluster_name, modifications):
        """
        PATCH /groups/{GROUP-ID}/clusters/{CLUSTER-NAME}
        https://docs.atlas.mongodb.com/reference/api/clusters-modify-one/
        :param project_id:
        :param cluster_name:
        :param modifications:  A dict defining the fields to be changed
        :return: a Change doc reflecting the updated cluster
        """

        return self.atlas_patch(f"/groups/{project_id}/clusters/{cluster_name}", data=modifications)

    @lru_cache(maxsize=500)
    def get_one_cached_cluster(self, project_id, cluster_name):
        return self.atlas_get(f"/groups/{project_id}/clusters/{cluster_name}")

    def get_one_cluster(self, project_id, cluster_name)->dict:
        return self.atlas_get(self.cluster_url(project_id, cluster_name))

    def pause(self, project_id, cluster_name):
        pause_doc = {"paused": True}
        return self.atlas_patch(f"/groups/{project_id}/clusters/{cluster_name}", pause_doc)

    def resume(self, project_id, cluster_name):
        pause_doc = {"paused": False}
        return self.atlas_patch(f"/groups/{project_id}/clusters/{cluster_name}", pause_doc)


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
        return f"AtlasAPI(api_key={self._api_key}, page_size={self._page_size})"





