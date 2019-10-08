#!/usr/bin/env python3

"""
MongoDB Atlas API (mongodbatlas)
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
from enum import Enum

from mongodbatlas.api import AtlasOrganization

from mongodbatlas.api import AtlasAPI,OutputFormat
from mongodbatlas.atlaskey import AtlasKey
from mongodbatlas.errors import AtlasGetError


class ParseError(ValueError):
    pass


class ResourceType(Enum):

    Project = "projects"
    Cluster = "clusters"

    def __str__(self):
        return self.value

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

    id1, separator, id2 = s.partition(sep)

    if separator != sep:
        raise ParseError(f"Bad separator '{separator}' in {s}")
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

    parser.add_argument("--publickey", help="MongoDB Atlas public API key")
    parser.add_argument("--privatekey", help="MongoDB Atlas private API key")

    parser.add_argument("--print_urls", default=False, action="store_true",
                        help="Print URLS constructed by API")
    parser.add_argument("--org", action="store_true", default=False,
                        help="Get the organisation associated with the "
                             "current API key pair [default: %(default)s]")
    parser.add_argument("--pause", default=[], dest="pause_cluster",
                        action="append", 
                        help="pause named cluster in project specified by project_id:cluster_name")
    parser.add_argument("--resume", default=[], 
                        dest="resume_cluster", action="append",
                        help="resume named cluster in project specified by project_id:cluster_name")
    parser.add_argument("--list", type=ResourceType, default=None, choices=list(ResourceType),
                        action="append",
                        help="List all of the reachable categories [default: %(default)s]")

    parser.add_argument("--ids", default=False, action="store_true", 
                        help="Report IDs as opposed to names")

    parser.add_argument('--cluster', default=[],
                        action="append", 
                        help="list all elements for for project_id:cluster_name")
    parser.add_argument("--project_id", default=[], dest="project_detail",
                        action="append",
                        help="specify project for cluster that is to be paused")
    parser.add_argument('--format', type=OutputFormat,
                        default=OutputFormat.SUMMARY, choices=list(OutputFormat),
                        help="The format to output data either in a single line "
                             "summary or a full JSON document [default: %(default)s]")
    parser.add_argument("--logging", default=False, action="store_true",
                        help="Turn on logging at debug level")
    parser.add_argument("--resource",
                        help="Get resource by URL can use a base URL like 'group'"
                             "or a full URL path")
    parser.add_argument("--itemsperpage", type=int, default=100,
                        help="No of items to return per page [default: %(default)s]")
    parser.add_argument("--pagenum", type=int, default=1,
                        help="Page to return [default: %(default)s]")
    args = parser.parse_args()

    if args.logging:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)

    logging.debug("logging is on at DEBUG level")

    if args.publickey:
        public_key = args.publickey
    else:
        public_key = os.getenv("ATLAS_PUBLIC_KEY")
        if public_key is None:
            print( "you must specify an ATLAS public key via --publickey arg "
                   "or the environment variable ATLAS_PUBLIC_KEY")
            sys.exit(10)

    if args.privatekey:
        private_key = args.privatekey
    else:
        private_key = os.getenv("ATLAS_PRIVATE_KEY")
        if private_key is None:
            print( "you must specify an an ATLAS private key via --privatekey"
                   "arg or the environment variable ATLAS_PRIVATE_KEY")
            sys.exit(1)

    api = AtlasAPI(AtlasKey(public_key, private_key))

    if args.resource:
        if args.resource == "root":
            r = api.atlas_get()
        elif args.resource.startswith("http"):
            r = api.get(args.resource, page_num=args.pagenum, items_per_page=args.itemsperpage)
        else:
            if not args.resource.startswith("/"):
                args.resource = f"/{args.resource}"
            r=api.atlas_get(args.resource, page_num=args.pagenum, items_per_page=args.itemsperpage)

        pprint.pprint(r)
        sys.exit(0)
    try:
        if args.org:
            print("Organisations:")
            for i in api.get_organization():
                i.print_resource(args.format)

        if ResourceType.Project in args.list:
            print("Projects:")
            for project in api.get_projects():
                project.print_resource(args.format)
            #print_links(project_links, api.get_project, project_details)

        if ResourceType.Cluster in args.list:
            print("Clusters:")
            for project in api.get_projects():
                for cluster in api.get_clusters(project.id):
                    cluster.print_resource(args.format)

        if args.pause_cluster:
            cluster_list_apply(api, args.pause_cluster, api.pause_cluster)

        if args.resume_cluster:
            cluster_list_apply(api, args.resume_cluster, api.resume_cluster)
        #
        # for i in args.cluster:
        #     project_id,sep,cluster_name = i.partition(":")
        #     if len(project_id) == len(i):
        #         print(f"Can't parse '{i}' as <project>:<cluster>")
        #         continue
        #     cluster = api.get_cluster(project_id, cluster_name)
        #     pprint.pprint(cluster)
    except KeyboardInterrupt:
        print("Ctrl-C: Exiting...")
