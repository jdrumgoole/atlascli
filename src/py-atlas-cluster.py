#!/usr/bin/env python3

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
import os
import pprint
import sys
import json
from mongodb_atlas_api import Atlas_API




def quote(s):
    return f"'{s}'"


def print_header():
    print("{:26}{:26}{:26}{:5}".format("Organisation", "Project", "Cluster", "Paused/Running"))


def print_atlas(org=None, project=None, cluster=None, paused=None):
    atlas_name = ""

    if org:
        atlas_name += "{:26}".format(org)

    if project:
        atlas_name += "{:26}".format(project)

    if cluster:
        atlas_name += "{:26}".format(cluster)

    if cluster:
        if paused:
            atlas_name += "{:4}".format("P")
        else:
            atlas_name += "{:4}".format("R")

    print(atlas_name)


def print_atlas_item(count, title, item, indent=0):
    print(" {}{}. {:5}: {:25} id={:>24}".format(" " * indent, count,  title, quote(item["name"]), item["id"]))


def print_atlas_cluster(count, title, item, indent=0):
    print(" {}{}. {:5}: {:25} id={:24} paused={}".format(" " * indent,
                                                         count,
                                                         title,
                                                         quote(item["name"]),
                                                         item["id"],
                                                         item["paused"]))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--username", help="MongoDB Atlas username")
    parser.add_argument("--apikey", help="MongoDB Atlas API key")
    parser.add_argument("--project_id", help="specify project for cluster that is to be paused")
    parser.add_argument("--org_id", help="specify an organisation to limit what is listed")
    parser.add_argument("--pause", default=[], dest="pause_cluster_name", action="append", help="pause named cluster in project specified by --project_id")
    parser.add_argument("--resume", default=[], dest="resume_cluster_name", action="append", help="resume named cluster in project specified by --project_id")
    parser.add_argument("--list", default=False, action="store_true", help="List of the complete org hierarchy")
    parser.add_argument("--ids", default=False, action="store_true", help="Report IDs as opposed to names")
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

    requester = Atlas_API(username, apikey)

    orgs=[]
    if args.list:
        if args.org_id:
            org = requester.get_one_org(args.org_id)
            orgs.append(org)
        else:
            orgs = requester.get_orgs()

        print_header()
        for org_count, org in enumerate(orgs, 1):
            # print_atlas(f"Org:{org['id']}")
            projects = requester.get_projects(org['id'])
            for project_count, project in enumerate(projects, 1):
                # print_atlas(f"Project:{project['id']}")
                try:
                    clusters = requester.get_clusters(project["id"])
                except requests.exceptions.HTTPError as e:
                    pprint.pprint(e)
                    continue
                for cluster_count, cluster in enumerate(clusters, 1):
                    try:
                        if args.ids:
                            print_atlas(org["id"], project["id"], cluster["name"], cluster["paused"])
                        else:
                            print_atlas(org["name"], project["name"], cluster["name"], cluster["paused"])

                    except requests.exceptions.HTTPError as e:
                        pprint.pprint(e)
                        continue

    for i in args.pause_cluster_name:
        if args.project_id:
            cluster = requester.get_one_cluster(args.project_id, i)
            requester.pause_cluster(args.project_id, cluster)

    for i in args.resume_cluster_name:
        if args.project_id:
            cluster = requester.get_one_cluster(args.project_id, i)
            requester.resume_cluster(args.project_id, cluster)
