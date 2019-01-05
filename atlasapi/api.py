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


class AtlasOrganizationAPI(AtlasAPIMixin):

    def __init__(self, username=None, api_key=None):
        super().__init__(username=username, api_key=api_key)

    def get_organization(self, organization_id):
        try:
            return AtlasOrganization(self.get_dict(f"/orgs/{organization_id}"))
        except HTTPError as e:
            raise AtlasRequestError(e)

    @lru_cache(maxsize=500)
    def get_cached_organization(self, organization_id):
        return AtlasOrganization(self.get_dict(f"/orgs/{organization_id}"))

    def get_organization_links(self):
        yield from self.get_linked_data("/orgs")

    def get_organisation_ids(self):
        yield from self.get_ids("orgs")

    def get_organisations(self):
        for i in self.get_linked_data("/orgs"):
            yield self.get_organization(i["id"])

    def __repr__(self):
        return f"{self.__class__.__name__}('{self._username}', '{self._api_key}')"


class AtlasProjectAPI(AtlasAPIMixin):

    def __init__(self, username=None, api_key=None):
        super().__init__(username=username, api_key=api_key)

    def get_project(self, project_id):
        return AtlasProject(self.get_dict(f"/groups/{project_id}"))

    @lru_cache(maxsize=500)
    def get_cached_project(self, project_id):
        return AtlasProject(self.get_dict(f"/groups/{project_id}"))

    def get_projects(self, organization_id):
        for i in self.get_linked_data(f"/orgs/{organization_id}/groups"):
            yield self.get_project(i["id"])


class AtlasClusterAPI(AtlasAPIMixin):

    def __init__(self, username=None, api_key=None):
        super().__init__(username=username, api_key=api_key)

    def get_cluster(self, project_id, cluster_name):
        return AtlasCluster(self.get_dict(self.cluster_url(project_id, cluster_name)))

    @lru_cache(maxsize=500)
    def get_cached_cluster(self, project_id, cluster_name):
        return self.get_dict(self.cluster_url(project_id, cluster_name))

    def get_clusters(self, project_id):
        for i in self.get_linked_data(f"/groups/{project_id}/clusters"):
            yield self.get_cluster(project_id, i["name"])



