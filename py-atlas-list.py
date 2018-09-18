#!/usr/bin/env python3
"""
List Orgs, Projects and Clusters (OPC) for
a MongoDB Atlas account denoted by a username
and an API Key.

Note this version only gets the first 100 items.
Link traversal comes later.

Joe.Drumgoole@mongodb.com
"""
import argparse
import requests
from requests.auth import HTTPDigestAuth
import json
import os
import pprint
import sys

class Atlas_API_Request(object):
    """
    Basic API class for listing MongoDB Atlas Assets
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

    def get_text(self, resource_url):
        return self.get(resource_url).text

    def get_dict(self, resource_url):
        t= self.get_text(resource_url)
        return json.loads(t)

    def get_orgs(self):
            return requester.get_dict(resource_url="/orgs")["results"]

    def get_projects(self, org_id):
        projects = requester.get_dict("/orgs/{}/groups".format(org_id))["results"]
        return projects

    def get_clusters(self, project_id):
        return self.get_dict("/groups/" + project_id + "/clusters")["results"]


def print_atlas_item(count, title, item, indent=0):
    print(" {}{}. {}: '{}' {}".format(" " * indent, count, title, item["name"], item["id"]))

def print_atlas_cluster(count, title, item, indent=0):
    print(" {}{}. {}: '{}' {} paused={}".format(" " * indent, count, title, item["name"], item["id"], item["paused"]))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--username", help="MongoDB Atlas username")
    parser.add_argument("--apikey", help="MongoDB Atlas API key")

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
