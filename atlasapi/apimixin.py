"""
Basic Python API to MongoDB Atlas Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@Author:Joe.Drumgoole@mongodb.com

"""
import os
import pprint
import logging
from logging import StreamHandler

from requests.auth import HTTPDigestAuth
import requests

from .atlaskey import AtlasKey
from .errors import AtlasRequestError, \
                    AtlasAuthenticationError,\
                    AtlasEnvironmentError,\
                    AtlasInitialisationError


class APIMixin(object):
    """
    Basic API class for accessing MongoDB Atlas Assets

    Also note that the terms projects and groups are used interchangeably
    between the API and the UI and are synonyms.
    """

    SITE_URL="https://cloud.mongodb.com"
    API_URL = f"/api/atlas/v1.0"
    ATLAS_BASE_URL=f"{SITE_URL}{API_URL}"

    ATLAS_HEADERS = {"Accept": "application/json",
                     "Content-Type": "application/json"}

    def __init__(self,
                 api_key:AtlasKey,
                 page_size=100,
                 debug=0):

        self._api_key: AtlasKey = api_key
        self._auth = None
        self._debug = None
        self._log = None
        self._page_size = page_size

        if self._page_size < 1 or self._page_size > 500 :
            raise AtlasInitialisationError("'page_size' must be between 1 and 500")


        if api_key:
            self._api_key = api_key
        else:
            self._api_key = AtlasKey.get_from_env()

        if debug:
            self._debug = debug
        else:
            atlas_debug_env = os.getenv("ATLAS_DEBUG", 0)
            try:
                self._debug = int(atlas_debug_env)
            except ValueError:
                raise AtlasEnvironmentError(f"Invalid value for ATLAS_DEBUG env: '{atlas_debug_env}'")

        if self._debug:
            self._log = logging.getLogger(__name__)

        # print(self._username)
        # print(self._api_key)
        self._auth = HTTPDigestAuth(self._api_key.public_key, self._api_key.private_key)

    def post(self, resource, data):

        if self._debug:
            self._log.debug(f"post({resource}, {data})")

        try:
            #print(f"atlas_post:{resource}, {data}")
            r = requests.post(resource, data=data, headers=self.ATLAS_HEADERS, auth=self._auth)
            print(r.url)
            r.raise_for_status()
            if self._log:
                self._log.debug(f"returns:")
                self._log.debug(f"\n{pprint.pprint(r.json())}")

        except requests.exceptions.HTTPError as e:
            raise AtlasRequestError(e)
        return r

    def get(self, resource, headers=None, auth=None):
        if self._debug:
            self._log.debug(f"get({resource})")
        # Need to use the raw URL when getting linked data

        assert self._api_key is not None
        assert self._api_key != ""
        assert self._username is not None
        assert self._username != ""

        r = requests.get(resource,
                         headers=headers,
                         auth=auth)
        r.raise_for_status()
        return r

    def atlas_post(self, resource, data):
        return self.post(f"{self.ATLAS_BASE_URL}{resource}", data)

    def atlas_get(self,resource):

        if self._debug:
            self._log.debug(f"get({resource})")
        # Need to use the raw URL when getting linked data
        if resource.startswith("http"):
            url = resource
        else:
            url = self.ATLAS_BASE_URL + resource

        assert self._api_key is not None
        assert self._api_key != ""
        assert self._username is not None
        assert self._username != ""

        try:

            r = requests.get(url=url,
                             headers=self.ATLAS_HEADERS,
                             auth=self._auth)
            r.raise_for_status()
            if self._log:
                self._log.debug(f"returns:")
                self._log.debug(f"\n{pprint.pprint(r.json())}")

        except requests.exceptions.HTTPError as e:
            raise AtlasRequestError(e)
        return r

    def patch(self, resource_url, patch_doc):
        p = requests.patch(self.ATLAS_BASE_URL + resource_url,
                           json=patch_doc,
                           headers=self.ATLAS_HEADERS,
                           auth=self._auth
                           )
        p.raise_for_status()
        return p

    def get_text(self, resource_url):
        return self.get(resource_url).text

    def get_dict(self, resource_url):
        return self.get(resource_url).json()

    def get_resource_by_page(self, resource):

        results = None
        next_link = None

        if self._log:
            self._log.debug(f"get_list_data_by_page({resource})")

        doc = self.get_dict(resource)

        if 'results' in doc:
            results = doc["results"]
        else:
            raise AtlasRequestError(f"No 'results' field in '{doc}'")

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
            raise AtlasRequestError(f"No 'results' field in '{doc}'")

    def get_resource_by_item(self, resource, limit=None):

        if self._log:
            self._log.debug(f"get_linked_data({resource})")

        doc = self.get_dict(resource)
        yield from self._get_results(doc)
        links = doc['links']
        last_link = links[-1]

        while "rel" in last_link and "next" == last_link["rel"]:
            doc = self.get_dict(last_link["href"])
            yield from self._get_results(doc)
            links = doc['links']
            last_link = links[-1]

        # links = doc['links']
        # last_link = links[-1]
        # # print(links)
        # # print(last_link)
        # if "rel" in last_link and "next" == last_link["rel"]:
        #     yield from self.get_resource_by_item(last_link["href"])

    def get_ids(self, field):
        for i in self.get_linked_data(f"/{field}"):
            yield i["id"]

    def get_names(self, field):
        for i in self.get_linked_data(f"/{field}"):
            yield i["name"]


class APIFormatter(object):

    def __init__(self, api):
        self._api = api
        self._spacing = 24

    @staticmethod
    def quote(s):
        return f"'{s}'"

    @staticmethod
    def print_cluster_summary_header():
        print("{:24} {:24} {:24}{:4}".format("Organisation", "Project", "Cluster", "Paused/Running"))

    @staticmethod
    def print_cluster_summary(org=None, project=None, cluster=None, paused=None, sep=" "):

        summary = f"{org:24}{sep}{project:24}{sep}{cluster:24}"

        if cluster:
            if paused:
                summary += "{:4}".format("P")
            else:
                summary += "{:4}".format("R")

        print(summary)

    # @staticmethod
    # def print_item(count, title, item, indent=0):
    #     print(" {}{}. {:5}: {:25} id={:>24}".format(" " * indent, count, title, quote(item["name"]), item["id"]))
    #
    # def print_clusterx_summary(count, title, item, indent=0):
    #     print(" {}{}. {:5}: {:25} id={:24} paused={}".format(" " * indent,
    #                                                          count,
    #                                                          title,
    #                                                          Atlas_API_Formatter.quote(item["name"]),
    #                                                          item["id"],
    #                                                          item["paused"]))

    def print_org_summary(self, org, ids=None):
        # print_atlas(f"Org:{org['id']}")
        projects = self._api.get_projects(org["id"])
        for project_count, project in enumerate(projects, 1):
            # print_atlas(f"Project:{project['id']}")
            try:
                clusters = self._api.get_clusters(project["id"])
            except requests.exceptions.HTTPError as e:
                pprint.pprint(e)
                continue
            for cluster_count, cluster in enumerate(clusters, 1):
                try:
                    if ids:
                        self.print_cluster_summary(org['id'],
                                                   project["id"],
                                                   cluster["name"],
                                                   cluster["paused"],
                                                   sep=":")
                    else:
                        self.print_cluster_summary(org["name"],
                                                   project["name"],
                                                   cluster["name"],
                                                   cluster["paused"],
                                                   sep=" ")

                except requests.exceptions.HTTPError as e:
                    pprint.pprint(e)
                    continue
