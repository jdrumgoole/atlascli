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

from datetime import datetime
from functools import lru_cache
import pprint
from enum import Enum

from dateutil import parser
from requests.exceptions import HTTPError

from mongodbatlas.apimixin import APIMixin
from mongodbatlas.atlaskey import AtlasKey


class OutputFormat(Enum):

    SUMMARY = "summary"
    FULL = "full"

    def __str__(self):
        return self.value


class AtlasResource(APIMixin):
    """
    Base class for Atlas Resources
    """
    def __init__(self, resource, api_key:AtlasKey=None):
        super().__init__(api_key)
        self._resource = resource
        if "created" in self._resource:  # convert date string to datetime obj
            self._resource["created"] = parser.parse(self._resource["created"])
        self._timestamp = datetime.utcnow()

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def id(self):
        return self._resource["id"]

    @property
    def name(self):
        return self._resource["name"]

    def summary_string(self):
        return f"id:'{self.id}' name:'{self.name}'"

    def print_resource(self, format=OutputFormat.SUMMARY):
        if format is OutputFormat.SUMMARY:
            print(self.summary_string())
        else:
            pprint.pprint(self._resource)

    def get_resource_by_item(self, resource):

        self._log.debug(f"get_linked_data({resource})")

        doc = self.atlas_get(resource)
        yield from self._get_results(doc)
        links = doc['links']
        last_link = links[-1]

        while "rel" in last_link and "next" == last_link["rel"]:
            doc = self.get(last_link["href"])
            yield from self._get_results(doc)
            links = doc['links']
            last_link = links[-1]

    def get_ids(self, field):
        for i in self.get_resource_by_item(f"/{field}"):
            yield i["id"]

    def get_names(self, field):
        for i in self.get_resource_by_item(f"/{field}"):
            yield i["name"]

    def __str__(self):
        return f'{pprint.pformat(self._resource)}'

    def __repr__(self):
        return f"{self.__class__.__name__}({self._resource!r})"


class AtlasOrganization(AtlasResource):

    def __init__(self, org):
        super().__init__(org)

    def get_organizations(self, limit=None):
        for org in self.get_resource_by_item("/orgs"):
            yield AtlasOrganization(org)

    def get_one_organization(self, org_id):
        return AtlasOrganization(self.atlas_get(f"/orgs/{org_id}"))

class AtlasProject(AtlasResource):

    def __init__(self, project):
        super().__init__(project)

    def get_projects(self, org_id):
        for project in self.get_linked_data(f"/orgs/{org_id}/groups"):
            yield AtlasProject(project)

    def get_one_project(self, project_id):
        return AtlasProject(self.atlas_get(f"/groups/{project_id}"))

class AtlasCluster(AtlasResource):

    def __init__(self, cluster):
        super().__init__(cluster)

    @staticmethod
    def cluster_url(project_id, cluster_name):
        return f"/groups/{project_id}/clusters/{cluster_name}"

    def summary_string(self):
        quoted_name = f"'{self.name}'"
        if self._resource['paused']:
            state = "paused"
        else:
            state = "running"
        return f"id:'{self.id}' name:{quoted_name:24} {state}"

    def get_clusters(self, project_id):
        for cluster in self.get_resource_by_item(f"/groups/{project_id}/clusters"):
            yield AtlasCluster(cluster)

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


class AtlasAPI(APIMixin):

    def __init__(self, api_key : AtlasKey=None):
        super().__init__(api_key)




    @lru_cache(maxsize=500)
    def get_cached_organization(self, organization_id):
        return AtlasOrganization(self.get(f"/orgs/{organization_id}"))

    def get_organization_links(self):
        """
        A generator that pages through all the results and returns each
        result an item at a time.

        :return: A generator with the link results.
        """
        yield from self.get_resource_by_item("/orgs")

    def get_organization_links_by_page(self):
        self._log.debug("get_organization_links_by_page()")
        """
        We provide `get_organization_links_by_page` to allow the client
        to catch exceptions and retry. With the generator API an exception
        will mean restarting the generator from scratch.

        :return: A tuple consistent of the list of results and the next
        URL to call for the next page of results. If there are no more
        results the URL value will be None.
        """
        return self.get_resource_by_page("/orgs")

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.api_key)})"

    def get_project(self, project_id):
            return AtlasProject(self.get(f"/groups/{project_id}"))

    @lru_cache(maxsize=500)
    def get_cached_project(self, project_id):
        return AtlasProject(self.get(f"/groups/{project_id}"))

    def get_projects(self):
        for i in self.get_resource_by_item("/groups"):
            yield AtlasProject(i)

    def get_project_ids(self):
        yield from self.get_ids("groups")

    def get_cluster(self, project_id, cluster_name):
        return AtlasCluster(self.get(f"/groups/{project_id}/clusters/{cluster_name}"))

    @lru_cache(maxsize=500)
    def get_cached_cluster(self, project_id, cluster_name):
        return self.get(f"/groups/{project_id}/clusters/{cluster_name}")

    def get_clusters(self, project_id):
        for i in self.get_resource_by_item(f"/groups/{project_id}/clusters"):
            yield AtlasCluster(i)


