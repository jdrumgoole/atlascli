"""
MongoDB Atlas Organisation
~~~~~~~~~~~~~~~~~~~~~~~~~~

An organisation is a top level artefact. Users can
create multiple organizations and be members of multiple
organizations. Each organization can have 0 or more
projects (also called groups) and each project can have 0 or
more
Author:joe@joedrumgoole.com
"""

from datetime import datetime
from functools import lru_cache
import pprint

from dateutil import parser
from requests.exceptions import HTTPError

from atlasapi.apimixin import AtlasAPIMixin
from atlasapi.errors import AtlasRequestError


class AtlasResource(object):

    def __init__(self, resource):
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

    def __str__(self):
        return f'{pprint.pformat(self._resource)}'

    def summary_string(self):
        return f"id:{self.id()}, name:{self.name()}"

    def print_summary(self):
        return self.summary_string()

    def __repr__(self):
        return f"{self.__class__.__name__}({self._resource!r})"


class AtlasOrganization(AtlasResource):

    def __init__(self, org):
        super().__init__(org)


class AtlasProject(AtlasResource):

    def __init__(self, project):
        super().__init__(project)


class AtlasCluster(AtlasResource):

    def __init__(self, cluster):
        super().__init__(cluster)


class AtlasAPI(AtlasAPIMixin):

    def __init__(self, username=None, api_key=None):
        super().__init__(username=username, api_key=api_key)

    def create_organization(self, name):

    def get_organization(self, organization_id):
        try:
            return AtlasOrganization(self.get_dict(f"/orgs/{organization_id}"))
        except HTTPError as e:
            raise AtlasRequestError(e)

    @lru_cache(maxsize=500)
    def get_cached_organization(self, organization_id):
        return AtlasOrganization(self.get_dict(f"/orgs/{organization_id}"))

    def get_organization_links(self):
        """
        A generator that pages through all the results and returns each
        result an item at a time.

        :return: A generator with the link results.
        """
        yield from self.get_resource_by_item("/orgs")

    def get_organization_links_by_page(self):
        """
        We provide `get_organization_links_by_page` to allow the client
        to catch exceptions and retry. With the generator API an exception
        will mean restarting the generator from scratch.

        :return: A tuple consistent of the list of results and the next
        URL to call for the next page of results. If there are no more
        results the URL value will be None.
        """
        return self.get_resource_by_page("/orgs")

    def get_organisation_ids(self):
        yield from self.get_ids("orgs")

    def get_organisations(self, limit=None):
        if limit:
            for i, org in enumerate(self.get_resource_by_item("/orgs"), 1):
                yield self.get_organization(org["id"])
                if i == limit:
                    break

    def __repr__(self):
        return f"{self.__class__.__name__}('{self._username}', '{self._api_key}')"

    def get_project(self, project_id):
        try:
            return AtlasProject(self.get_dict(f"/groups/{project_id}"))
        except HTTPError as e:
            raise AtlasRequestError(e)

    @lru_cache(maxsize=500)
    def get_cached_project(self, project_id):
        return AtlasProject(self.get_dict(f"/groups/{project_id}"))

    def get_project_links(self):
        yield from self.get_resource_by_item("/groups")

    def get_project_ids(self):
        yield from self.get_ids("groups")

    def get_projects(self, organization_id):
        for i in self.get_resource_by_item(f"/orgs/{organization_id}/groups"):
            yield self.get_project(i["id"])

    def get_cluster(self, project_id, cluster_name):
        return AtlasCluster(self.get_dict(f"/groups/{project_id}/clusters/{cluster_name}"))

    @lru_cache(maxsize=500)
    def get_cached_cluster(self, project_id, cluster_name):
        return self.get_dict(f"/groups/{project_id}/clusters/{cluster_name}")

    def get_clusters(self, project_id):
        for i in self.get_resource_by_item(f"/groups/{project_id}/clusters"):
            yield self.get_cluster(project_id, i["name"])

    def pause_cluster(self, org_id, cluster):

        name = cluster['name']
        if cluster["paused"]:
            print(f"Cluster: '{name}' is already paused. Nothing to do")
        else:
            print(f"Pausing cluster: '{name}'")
            pause_doc = {"paused": True}
            self.patch(f"/groups/{org_id}/clusters/{name}", pause_doc)

    def resume_cluster(self, org_id, cluster):

        name = cluster['name']
        if not cluster["paused"]:
            print(f"Cluster: '{name}' is already running. Nothing to do")
        else:
            print(f"Resuming cluster: '{name}'")
            pause_doc = {"paused": False}
            self.patch(f"/groups/{org_id}/clusters/{name}", pause_doc)
