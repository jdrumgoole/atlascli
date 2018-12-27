#!/usr/bin/env python3

"""
MongoDB Atlas API (atlasapi)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python API to MongoDB Atlas.

Author: Joe.Drumgoole@mongodb.com
"""
import argparse
import requests
import os
import pprint
import sys

from atlasapi.api import API, APIFormatter


class ParseError(ValueError):
    pass


def parse_id(s, sep=":"):
    """

    :param s: A sting of the form <id1>:<id2> used to specify an ID tuple
    typically used to specify a project and cluster_name.
    :param sep: Seperator string used for two parts of s. Default is ':'.
    :return: id1,id2

    Throws ParseError if strings do not split on a sep of ':'.

    >>> parse_id("xxxx:yyyy")
    ('xxxx', 'yyyy')
    >>>
    """

    id1, seperator, id2 = s.partition(sep)

    if seperator != sep:
        raise ParseError(f"Bad seperator '{seperator}'in {s}")
    return id1, id2


def cluster_list_apply(api, clusters, op_func):
    for i in clusters:
        try:
            project_id, cluster_name = parse_id(i)
        except ParseError:
            print(f"Error: Can't parse '{i}'")
            continue
        try:
            cluster = api.get_one_cluster(project_id, cluster_name)
            op_func(project_id, cluster)
        except requests.exceptions.HTTPError as e:
            print("Error:Atlas API request failed")
            print(e)
            continue


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--username", help="MongoDB Atlas username")
    parser.add_argument("--apikey", help="MongoDB Atlas API key")

    parser.add_argument("--print_urls", default=False, action="store_true",
                        help="Print URLS constructed by API")
    parser.add_argument("--org_id", 
                        help="specify an organisation to limit what is listed")
    parser.add_argument("--pause", default=[], dest="pause_cluster",
                        action="append", 
                        help="pause named cluster in project specified by project_id:cluster_name")
    parser.add_argument("--resume", default=[], 
                        dest="resume_cluster", action="append",
                        help="resume named cluster in project specified by project_id:cluster_name")
    parser.add_argument("--list", default=False, action="store_true", 
                        help="List of the complete org hierarchy")
    parser.add_argument("--ids", default=False, action="store_true", 
                        help="Report IDs as opposed to names")
    parser.add_argument('--cluster', default=[], dest="cluster_detail", 
                        action="append", 
                        help="list all elements for for project_id:cluster_name")
    parser.add_argument("--project_id", default=[], dest="project_detail",
                        action="append",
                        help="specify project for cluster that is to be paused")
    parser.add_argument("--output", dest="output_filename",
                        default="atlasapi.out",
                        help="Send output to a file [ default: %(default)s]")
    
    args = parser.parse_args()

    if args.username:
        username = args.username
    else:
        username = os.getenv("ATLAS_USERNAME")
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

    api = API(username, apikey, args.print_urls)
    formatter = APIFormatter(api)

    orgs = []
    if args.list:
        if args.org_id:
            org = api.get_one_org(args.org_id)
            orgs.append(org)
        else:
            orgs = api.get_orgs()

        for i, index in enumerate(orgs, 1):
            print(index)
            formatter.print_org(i)
            #formatter.print_cluster_summary_header()
            #formatter.print_org_summary(i, args.ids)

        # print_header()
        # for org_count, org in enumerate(orgs, 1):
        #     # print_atlas(f"Org:{org['id']}")
        #     projects = api.get_projects(org['id'])
        #     for project_count, project in enumerate(projects, 1):
        #         # print_atlas(f"Project:{project['id']}")
        #         try:
        #             clusters = api.get_clusters(project["id"])
        #         except requests.exceptions.HTTPError as e:
        #             pprint.pprint(e)
        #             continue
        #         for cluster_count, cluster in enumerate(clusters, 1):
        #             try:
        #                 if args.ids:
        #                     print_atlas(org["id"], project["id"], cluster["name"], cluster["paused"])
        #                 else:
        #                     print_atlas(org["name"], project["name"], cluster["name"], cluster["paused"])
        #
        #             except requests.exceptions.HTTPError as e:
        #                 pprint.pprint(e)
        #                 continue

    cluster_list_apply(api, args.pause_cluster, api.pause_cluster)
    cluster_list_apply(api, args.resume_cluster, api.resume_cluster)
    # for i in args.resume_cluster:
    #     try:
    #         project_id, cluster_name = parse_id(i)
    #     except ParseError:
    #         print(f"Error: Can't parse '{i}'")
    #         continue
    #     cluster = api.get_one_cluster(project_id, i)
    #     api.resume_cluster(project_id, cluster)
            
    for i in args.cluster_detail:
        project_id,sep,cluster_name = i.partition(":")
        if len(project_id) == len(i):
            print(f"Can't parse '{i}' as <project>:<cluster>")
            continue
        cluster = api.get_one_cluster(project_id, cluster_name)
        pprint.pprint(cluster)
