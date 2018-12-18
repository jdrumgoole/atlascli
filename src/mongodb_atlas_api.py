"""
Basic Python API to some Atlas Services

@Author:Joe.Drumgoole@mongodb.com

"""

from requests.auth import HTTPDigestAuth
import requests
import os


class MongoDBAtlasAPI(object):
    """
    Basic API class for accessing MongoDB Atlas Assets
    Note that this doesn't follow links right now so it will only get
    the first 100 orgs, projects and/or clusters.

    Also note that the terms projects and groups are used interchangeably
    between the API and the UI and are synonyms.
    """

    BASE_URL = "https://cloud.mongodb.com/api/atlas/v1.0"
    HEADERS = {"Accept": "application/json",
               "Content-Type": "application/json"}

    def __init__(self, username=None, api_key=None, print_urls=None):

        if username:
            self._username = username
        else:
            username = os.getenv("ATLAS_USERNAME")
            if username is None:
                raise ValueError("you must specify a username (try using the environment variable ATLAS_USERNAME)")
            else:
                self._username = username

        if api_key:
            self._api_key = api_key
        else:
            self._api_key = os.getenv("ATLAS_APIKEY")
            if self._api_key is None:
                raise ValueError("you must specify an apikey (try using the environment variable ATLAS_APIKEY)")
            else:
                self._api_key = api_key

        self._print_urls = print_urls

        self._auth = HTTPDigestAuth(self._username, self._api_key)

    def get(self, resource_url):

        # Need to use the raw URL when getting linked data
        if resource_url.startswith("http"):
            url = resource_url
        else:
            url = MongoDBAtlasAPI.BASE_URL+resource_url

        r = requests.get(url=url,
                         headers=MongoDBAtlasAPI.HEADERS,
                         auth=self._auth)
        if self._print_urls:
            print("request URL: '{}'".format(r.url))
        r.raise_for_status()
        return r

    def patch(self, resource_url, patch_doc):
        p = requests.patch(MongoDBAtlasAPI.BASE_URL + resource_url,
                           json=patch_doc,
                           headers=MongoDBAtlasAPI.HEADERS,
                           auth=self._auth
                           )
        p.raise_for_status()

    def get_text(self, resource_url):
        return self.get(resource_url).text

    def get_dict(self, resource_url):
        return self.get(resource_url).json()

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

    def get_orgs(self):
        yield from self.get_linked_data("/orgs")

    def get_one_org(self, org_id):
        return self.get_dict(f"/orgs/{org_id}")

    def get_projects(self, org):
        yield from self.get_linked_data(f"/orgs/{org['id']}/groups")

    def get_one_project(self, project_id):
        return self.get_dict(f"/groups/{project_id}")

    def get_clusters(self, project_id):
        yield from self.get_linked_data(f"/groups/{project_id}/clusters")

    def get_one_cluster(self, project_id, cluster_name):
        return self.get_dict(MongoDBAtlasAPI.cluster_url(project_id, cluster_name))

    def pause_cluster(self, org_id, cluster):

        if cluster["paused"]:
            print(f"Cluster: {cluster['name']} is already paused. Nothing to do")
        else:
            print(f"Pausing cluster: {cluster['name']}")
            pause_doc = {"paused": True}
            self.patch(MongoDBAtlasAPI.cluster_url(org_id, cluster["name"]), pause_doc)

    def resume_cluster(self, org_id, cluster):

        if not cluster["paused"]:
            print(f"Cluster: {cluster['name']} is already running. Nothing to do")
        else:
            print(f"Resuming cluster: {cluster['name']}")
            pause_doc = {"paused": False}
            self.patch(MongoDBAtlasAPI.cluster_url(org_id, cluster["name"]), pause_doc)
