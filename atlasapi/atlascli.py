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
import logging

from atlasapi.api import AtlasOrganization

from atlasapi.api import AtlasAPI
from atlasapi.errors import AtlasAuthenticationError, AtlasRequestError


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


def print_links(resource_links, resource_item, details=None, counter=1):

    for i, link in enumerate(resource_links, counter):
        print(f"{i}. id:'{link['id']}', name:'{link['name']}'")
        if details:
            try:
                print(resource_item(link['id']))
            except AtlasRequestError as e:
                print(f"Can't get info for resource ID: '{link['id']}' error:{e}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--username", help="MongoDB Atlas username")
    parser.add_argument("--apikey", help="MongoDB Atlas API key")

    parser.add_argument("--print_urls", default=False, action="store_true",
                        help="Print URLS constructed by API")
    parser.add_argument("--org-id",dest="org_ids", default=[], action="append",
                        help="specify an organisation to limit what is listed")
    parser.add_argument("--pause", default=[], dest="pause_cluster",
                        action="append", 
                        help="pause named cluster in project specified by project_id:cluster_name")
    parser.add_argument("--resume", default=[], 
                        dest="resume_cluster", action="append",
                        help="resume named cluster in project specified by project_id:cluster_name")
    parser.add_argument("--list", default=[], choices=["orgs", "projects", "clusters"],
                        action="append",
                        help="List all of the reachable categories")
    parser.add_argument("--details", default=[], action="append",
                        choices=["orgs", "projects", "clusters"],
                        help="Print of details for each organisation [default: %(default)s]")
    parser.add_argument("--ids", default=False, action="store_true", 
                        help="Report IDs as opposed to names")

    parser.add_argument('--cluster', default=[],
                        action="append", 
                        help="list all elements for for project_id:cluster_name")
    parser.add_argument("--project_id", default=[], dest="project_detail",
                        action="append",
                        help="specify project for cluster that is to be paused")
    parser.add_argument("--output", dest="output_filename",
                        default="atlasapi.out",
                        help="Send output to a file [default: %(default)s]")

    parser.add_argument("--logging", default=False, action="store_true",
                        help="Turn on logging at debug level")
    args = parser.parse_args()

    if args.logging:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)

    logging.debug("logging is on at DEBUG level")

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

    api = AtlasAPI(username, apikey)

    org_details = "orgs" in args.details
    project_details = "projects" in args.details
    cluster_details = "clusters" in args.details

    #formatter = APIFormatter(api)

    try:
        org_links = []
        if "orgs" in args.list:
            if args.org_ids:
                for i in args.org_ids:
                    org = api.get_organization(i)
                    print(org)
            else:
                org_links = api.get_organization_links()
                print_links(org_links, api.get_organization, org_details)
            # for i, org_link in enumerate(org_links, 1):
            #     print(f"{i}. id:'{org_link['id']}', name:'{org_link['name']}'")
            #     if args.org_details:
            #         try:
            #             org = api.get_organization(org_link['id'])
            #             print(org)
            #         except AtlasRequestError as e:
            #             print(f"Can't get info for organization ID: '{org_link['id']}' error:{e}")
            if "projects" in args.list:
                project_links = api.get_project_links()
                print_links(project_links, api.get_project, cluster_details)

        elif "projects" in args.list:
            project_links = api.get_project_links()
            print_links(project_links, api.get_project, project_details)

        if args.pause_cluster:
            cluster_list_apply(api, args.pause_cluster, api.pause_cluster)

        if args.resume_cluster:
            cluster_list_apply(api, args.resume_cluster, api.resume_cluster)

        # for i in args.resume_cluster:
        #     try:
        #         project_id, cluster_name = parse_id(i)
        #     except ParseError:
        #         print(f"Error: Can't parse '{i}'")
        #         continue
        #     cluster = api.get_one_cluster(project_id, i)
        #     api.resume_cluster(project_id, cluster)

        for i in args.cluster:
            project_id,sep,cluster_name = i.partition(":")
            if len(project_id) == len(i):
                print(f"Can't parse '{i}' as <project>:<cluster>")
                continue
            cluster = api.get_cluster(project_id, cluster_name)
            pprint.pprint(cluster)
    except KeyboardInterrupt:
        print("Ctrl-C: Exiting...")
