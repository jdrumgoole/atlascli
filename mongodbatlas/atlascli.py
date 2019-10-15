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
import json
from enum import Enum


from mongodbatlas.apimixin import OutputFormat
from mongodbatlas.api import API
from mongodbatlas.atlaskey  import AtlasKey
from mongodbatlas.errors import AtlasGetError, AtlasError


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


class ClusterState(Enum):
    PAUSE="pause"
    RESUME="resume"

    def __str__(self):
        return self.value


class HTTPOperation(Enum):
    GET="get"
    POST="post"
    PATCH="patch"

    def __str__(self):
        return self.value


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--publickey", help="MongoDB Atlas public API key")
    parser.add_argument("--privatekey", help="MongoDB Atlas private API key")

    parser.add_argument("--org", action="store_true", default=False,
                        help="Get the organisation associated with the "
                             "current API key pair [default: %(default)s]")
    parser.add_argument("--pause", default=[], dest="pause_cluster",
                        action="append", 
                        help="pause named cluster in project specified by project_id "
                             "Note that clusters that have been resumed cannot be paused"
                             "for the next 60 minutes")
    parser.add_argument("--resume", default=[],
                        dest="resume_cluster", action="append",
                        help="resume named cluster in project specified by project_id")
    parser.add_argument("--list", type=ResourceType, default=None, choices=list(ResourceType),
                        action="append",
                        help="List all of the reachable categories [default: %(default)s]")

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
    parser.add_argument("--debug", default=False, action="store_true",
                        help="Turn on logging at debug level")
    parser.add_argument("--http", type=HTTPOperation, choices=list(HTTPOperation),
                        help="do a http operation")
    parser.add_argument("--url", help="URL for HTTP operation")
    parser.add_argument("--data", help="Data for HTTP operation")
    parser.add_argument("--itemsperpage", type=int, default=100,
                        help="No of items to return per page [default: %(default)s]")
    parser.add_argument("--pagenum", type=int, default=1,
                        help="Page to return [default: %(default)s]")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

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

    api = API(AtlasKey(public_key, private_key))

    try:
        r = None
        if args.http:
            if args.http == HTTPOperation.GET:
                r = api.get(args.url)
            elif args.http == HTTPOperation.POST:
                if args.data:
                    r = api.post(args.url, data=json.loads(args.data))
            elif args.http == HTTPOperation.PATCH:
                if args.data:
                    r = api.post(args.url, data=json.loads(args.data))
            if r is None:
                print("No response")
            else:
                pprint.pprint(r)
            # if args.httpget == "root":
            #     r = api.atlas_get()
            # elif args.httpget.startswith("http"):
            #     r = api.get(args.httpget, page_num=args.pagenum, items_per_page=args.itemsperpage)
            # else:
            #     if not args.httpget.startswith("/"):
            #         args.httpget = f"/{args.httpget}"
            #     r=api.atlas_get(args.httpget, page_num=args.pagenum, items_per_page=args.itemsperpage)
            #

        else:
            if args.org:
                print("Organisations:")
                for i in api.get_organizations():
                    i.print_resource(args.format)

            if args.list and ResourceType.Project in args.list:
                print("Projects:")
                for project in api.get_projects():
                    project.print_resource(args.format)
                #print_links(project_links, api.get_project, project_details)

            if args.list and ResourceType.Cluster in args.list:
                print("Clusters:")
                for project in api.get_projects():
                    for cluster in api.get_clusters(project.id):
                        cluster.print_resource(args.format)

            if args.pause_cluster:
                for i in args.pause_cluster:
                    for project in api.get_projects():
                        for cluster in api.get_clusters(project.id):
                            if cluster.id == i :
                                result = api.pause(cluster.id)
                                if result is None:
                                    print(f"Cluster {cluster.id} {cluster.name} was already paused")
                                else:
                                    print(f"Pausing {cluster.id} {cluster.name}")

            if args.resume_cluster:
                for i in args.resume_cluster:
                    for project in api.get_projects():
                        for cluster in api.get_clusters(project.id):
                            if cluster.id == i:
                                result = cluster.resume(cluster.id)
                                if result is None:
                                    print(f"Cluster {cluster.id} {cluster.name} was already running")
                                else:
                                    print(f"Resuming  {cluster.id} {cluster.name}")

    except KeyboardInterrupt:
        print("Ctrl-C: Exiting...")
    except AtlasError as e:
        print(f"AtlasError:{e}")

if __name__ == "__main__":
    main()
