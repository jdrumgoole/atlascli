"""
Dump Orgs, Projects and Clusters (OPC) for
a MongoDB Atlas account denoted by a username
and an API Key.

Allow pausing and resuming of named clusters

Joe.Drumgoole@mongodb.com
"""
import argparse
import requests
from requests.auth import HTTPDigestAuth
import json
import os
import pprint

class Atlas_API_Request(object):
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
        r = requests.get( Atlas_API_Request.BASE_URL+resource_url,
                          headers=Atlas_API_Request.HEADERS,
                          auth=self._auth)
        if self._print_urls:
            print("request URL: '{}'".format(r.url))
        r.raise_for_status()
        return r

    def patch(self, resource_url, patch_doc):
        p = requests.patch( Atlas_API_Request.BASE_URL+resource_url,
                            json=patch_doc,
                            headers=Atlas_API_Request.HEADERS,
                            auth=self._auth
                            )
        p.raise_for_status()


    def get_json(self, resource_url):
        return self.get(resource_url).json()

    def get_text(self, resource_url):
        return self.get(resource_url).text

    def get_dict(self, resource_url):
        t= self.get_text(resource_url)
        return json.loads(t)

    def cluster_url(self, project_id, cluster_name):
        return "/groups/" + project_id + "/clusters/" + cluster_name

    def get_orgs(self):
            return requester.get_dict(resource_url="/orgs")["results"]

    def get_one_org(self, org_id):
        return requester.get_dict(resource_url="/orgs/{}".format(org_id))

    def get_projects(self, org_id):
        projects = requester.get_dict("/orgs/{}/groups".format(org_id))["results"]
        return projects

    def get_one_project(self, project_id):
        return requester.get_dict(resource_url="/groups/{}".format(args.project_id))

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
            requester.patch(requester.cluster_url(org_id, cluster["name"]), pause_doc)

    def resume_cluster(self, org_id, cluster):

        if cluster["paused"] == False:
            print("Cluster: '{}' is already running. Nothing to do".format(cluster["name"]))
        else:
            print("Resuming cluster: '{}'".format(cluster["name"]))
            assert cluster["paused"] == True
            pause_doc = {"paused":False}
            requester.patch(requester.cluster_url(org_id, cluster["name"]), pause_doc)

def print_atlas_item(count, title, item, indent=0):
    print(" {}{}. {}: '{}' {}".format(" " * indent, count, title, item["name"], item["id"]))

def print_atlas_cluster(count, title, item, indent=0):
    print(" {}{}. {}: '{}' {} paused={}".format(" " * indent, count, title, item["name"], item["id"], item["paused"]))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--username", help="MongoDB Atlas username")
    parser.add_argument("--apikey", help="MongoDB Atlas API key")
    parser.add_argument("--project_id", help="specify project for cluster that is to be paused")
    parser.add_argument("--pause", dest="pause_cluster_name", help="pause named cluster in project specified by --project_id")
    parser.add_argument("--resume",  dest="resume_cluster_name", help="resume named cluster in project specified by --project_id")
    parser.add_argument("--list", default=False, action="store_true", help="List of the complete org hierarchy")

    args = parser.parse_args()

    if args.username:
        username = args.username
    else:
        username = os.getenv( "ATLAS_USERNAME")
        if username is None:
            print( "you must specify a username (via --username or the env ATLAS_USERNAME)")
            sys.exit(10)

    if args.apikey:
        apikey = args.apikey
    else:
        apikey = os.getenv("ATLAS_APIKEY")
        if apikey is None:
            print( "you must specify an apikey (via --apikey or te env ATLAS_APIKEY)")
            sys.exit(1)

    requester = Atlas_API_Request(username, apikey)

    if args.list:
        orgs = requester.get_orgs()
        for org_count, org in enumerate(orgs, 1):
            print_atlas_item(org_count, "Org", org)
            projects = requester.get_projects(org["id"])
            for project_count, project in enumerate(projects, 1):
                print_atlas_item(project_count, "Proj", project, 1)
                try:
                    clusters = requester.get_clusters(project["id"])
                except requests.exceptions.HTTPError as e:
                    pprint.pprint(e)
                    continue
                for cluster_count, cluster in enumerate(clusters, 1):
                    try:
                        print_atlas_cluster(cluster_count, "cluster", cluster, 2)
                    except requests.exceptions.HTTPError as e:
                        pprint.pprint(e)
                        continue

    if args.pause_cluster_name:
        cluster = requester.get_one_cluster(args.project_id, args.pause_cluster_name)
        requester.pause_cluster(args.project_id, cluster)

    if args.resume_cluster_name:
        cluster = requester.get_one_cluster(args.project_id, args.resume_cluster_name)
        requester.resume_cluster(args.project_id, cluster)
