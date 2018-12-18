"""
Dump Orgs, Projects and Clusters (OPC) for
a MongoDB Atlas account denoted by a username
and an API Key.

Allow pausing and resuming of named clusters

Joe.Drumgoole@mongodb.com
"""
import argparse
import requests
from mongodb_atlas_api import MongoDBAtlasAPI
import os
import pprint

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

    requester = MongoDBAtlasAPI(username, apikey)

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
