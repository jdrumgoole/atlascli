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
from mongodb_atlas_api import MongoDBAtlasAPI
import os
import pprint
import sys


def quote(s):
    return "'{}',".format(s)


def print_atlas_item(count, title, item, indent=0):
    print(" {}{:3}. {:5}: {:25} id={:>24}".format(" " * indent, count,  title, quote(item["name"]), item["id"]))


def print_atlas_cluster(count, title, item, indent=0):
    print(" {}{:3}. {:5}: {:25} id={:24} paused={}".format(" " * indent, count, title, quote(item["name"]), item["id"], item["paused"]))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--username", help="MongoDB Atlas username")
    parser.add_argument("--apikey", help="MongoDB Atlas API key")
    parser.add_argument("--org_id", help="specify an organization to limit what is listed")
    parser.add_argument("--orgs", default=True, help="List all the orgs for a user")
    parser.add_argument("--projects", help="List projects for an org")
    parser.add_argument("--clusters", help="List clusters for a project")

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

    requester = MongoDBAtlasAPI(username, apikey)

    orgs = []
    if args.org_id:
        org = requester.get_one_org(args.org_id)
        orgs.append(org)
    else:
        try:
            orgs = requester.get_orgs()
        except requests.exceptions.HTTPError as e:
            pprint.pprint(e)

        if args.orgs:
            for org_count, org in enumerate(orgs, 1):
                print_atlas_item(org_count, "Org", org)
                if args.projects:
                    try:
                        projects = requester.get_projects(org["id"])
                    except requests.exceptions.HTTPError as e:
                        pprint.pprint(e)
                        continue
                    for project_count, project in enumerate(projects, 1):
                        print_atlas_item(project_count, "Proj", project, 1)
                        if args.clusters:
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
