"""
Basic Python API to MongoDB Atlas Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@Author:Joe.Drumgoole@mongodb.com

"""

from requests.auth import HTTPDigestAuth
from requests.exceptions import HTTPError
import requests
import os
import pprint


class AtlasAuthenticationError(ValueError):
    pass

class AtlasRequestError(ValueError):
    pass

class AtlasAPIMixin(object):
    """
    Basic API class for accessing MongoDB Atlas Assets

    Also note that the terms projects and groups are used interchangeably
    between the API and the UI and are synonyms.
    """

    ATLAS_BASE_URL = "https://cloud.mongodb.com/api/atlas/v1.0"
    ATLAS_HEADERS = {"Accept": "application/json",
                     "Content-Type": "application/json"}

    def __init__(self, username=None, api_key=None, print_urls=None):
        self._api_key = None
        self._username = None
        self._api_key = None
        self._auth = None
        self._print_urls = False

        if username:
            self._username = username
        else:
            username = os.getenv("ATLAS_USERNAME")
            if username is None:
                raise AtlasAuthenticationError("you must specify a username (try using the environment variable ATLAS_USERNAME)")
            else:
                self._username = username

        if api_key:
            self._api_key = api_key
        else:
            self._api_key = os.getenv("ATLAS_APIKEY")
            if self._api_key is None:
                raise AtlasAuthenticationError("you must specify an apikey (try using the environment variable ATLAS_APIKEY)")

        self._print_urls = print_urls

        # print(self._username)
        # print(self._api_key)
        self._auth = HTTPDigestAuth(self._username, self._api_key)

    def get(self, resource_url):

        # Need to use the raw URL when getting linked data
        if resource_url.startswith("http"):
            url = resource_url
        else:
            url = self.ATLAS_BASE_URL + resource_url

        assert self._api_key is not None
        assert self._api_key != ""
        assert self._username is not None
        assert self._username != ""

        try:
            r = requests.get(url=url,
                             headers=self.ATLAS_HEADERS,
                             auth=self._auth)
            if self._print_urls:
                print("request URL: '{}'".format(r.url))
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise AtlasRequestError(f"Atlas Request Error: '{r.url}'")
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
        try:
            return self.get(resource_url).json()
        except HT

    def get_linked_data(self, resource):
        # print("get_linked_data")
        doc = self.get_dict(resource)

        if 'results' in doc:
            for i in doc["results"]:
                yield i
        else:
            raise ValueError(f"No 'results' field in '{doc}'")
        links = doc['links']
        last_link = links[-1]
        # print(links)
        # print(last_link)
        if "rel" in last_link and "next" == last_link["rel"]:
            yield from self.get_linked_data(last_link["href"])

    @staticmethod
    def cluster_url(project_id, cluster_name):
        return f"/groups/{project_id}/clusters/{cluster_name}"

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

    def print_org(self, org):
        print(org)

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
