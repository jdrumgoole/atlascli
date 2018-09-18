"""
Basic Python API to some Atlas Services

@Author:Joe.Drumgoole@mongodb.com

"""

import json
import requests

class Atlas_API(object):
    """
    Basic API class for accessing MongoDB Atlas Assets
    Note that this doesn't follow links right now so it will only get
    the first 100 orgs, projects and/or clusters.
    """

    BASE_URL = "https://cloud.mongodb.com/api/atlas/v1.0"
    HEADERS  = { "Accept"       : "application/json",
                 "Content-Type" : "application/json" }

    def __init__(self, username, apikey, print_urls=None ):
        self._username = username
        self._apikey = apikey
        self._print_urls = print_urls

        self._auth  = HTTPDigestAuth(self._username, self._apikey)


    def get(self, resource_url):
        r = requests.get(Atlas_API.BASE_URL + resource_url,
                         headers=Atlas_API.HEADERS,
                         auth=self._auth)
        if self._print_urls:
            print("request URL: '{}'".format(r.url))
        r.raise_for_status()
        return r

    def patch(self, resource_url, patch_doc):
        p = requests.patch(Atlas_API.BASE_URL + resource_url,
                           json=patch_doc,
                           headers=Atlas_API.HEADERS,
                           auth=self._auth
                           )
        p.raise_for_status()


    def get_json(self, rxesource_url):
        return self.get(resource_url).json()

    def get_text(self, resource_url):
        return self.get(resource_url).text

    def get_dict(self, resource_url):
        t= self.get_text(resource_url)
        return json.loads(t)

    def cluster_url(self, project_id, cluster_name):
        return "/groups/" + project_id + "/clusters/" + cluster_name

    def get_orgs(self):
            return self.get_dict(resource_url="/orgs")["results"]

    def get_one_org(self, org_id):
        return self.get_dict(resource_url="/orgs/{}".format(org_id))

    def get_projects(self, org_id):
        projects = self.get_dict("/orgs/{}/groups".format(org_id))["results"]
        return projects

    def get_one_project(self, project_id):
        return self.get_dict(resource_url="/groups/{}".format(args.project_id))


    def get_clusters(self, project_id):
        return self.get_dict("/groups/" + project_id + "/clusters")["results"]

    def get_one_cluster(self, project_id, cluster_name):
        return self.get_dict(self.cluster_url(project_id, cluster_name))

    def pause_cluster(self, org_id, cluster):

        if cluster["paused"] == True:
            print("Cluster: '{}' is already paused. Nothing to do".format(cluster["name"]))
        else:
            print("Pausing cluster: '{}'".format(cluster["name"]))
            assert cluster["paused"] == False
            pause_doc = {"paused" : True}
            self.patch(self.cluster_url(org_id, cluster["name"]), pause_doc)

    def resume_cluster(self, org_id, cluster):

        if cluster["paused"] == False:
            print("Cluster: '{}' is already running. Nothing to do".format(cluster["name"]))
        else:
            print("Resuming cluster: '{}'".format(cluster["name"]))
            assert cluster["paused"] == True
            pause_doc = {"paused":False}
            self.patch(self.cluster_url(org_id, cluster["name"]), pause_doc)
