#!/usr/bin/env python3

"""
MongoDB Atlas API (atlascli)
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
from typing import List
from datetime import datetime
import json
from typing import Dict

from colorama import init, Fore

from atlascli.atlaskey import AtlasKey
from atlascli.errors import AtlasError, AtlasGetError
from atlascli.atlasapi import AtlasAPI
from atlascli.version import __VERSION__
from atlascli.atlasorganization import AtlasOrganization
from atlascli.atlascluster import AtlasCluster


class ParseError(ValueError):
    pass


def parse_id(s: str, sep: str = ":") -> tuple:
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

    # class ClusterState(Enum):
    #     PAUSE = "pause"
    #     RESUME = "resume"

    #     def __str__(self):
    #         return self.value

    # class HTTPOperationName(Enum):
    #     GET = "get"
    #     POST = "post"
    #     PATCH = "patch"

    #     def __str__(self):
    #         return self.value

    # class AtlasOperationName(Enum):
    #     CREATE = "create"
    #     PATCH = "patch"
    #     DELETE = "delete"
    #     LIST = "list"
    #     PAUSE = "pause"
    #     RESUME = "resume"

    #     def __str__(self):
    #         return self.value

    # class AtlasResourceName(Enum):
    #     ORGANIZATION = "organization"
    #     PROJECT = "project"
    #     CLUSTER = "cluster"

    def __str__(self):
        return self.value


def pause_cluster(c: AtlasCluster):
    if c.is_paused():
        print(f"Cluster '{c.name}' is already paused")
    else:
        print(f"Trying to pause: '{c.name}'")
        c.pause()

        print(f"Paused cluster '{c.name}' at {datetime.now().strftime('%H:%M:%S')}")


def resume_cluster(c: AtlasCluster):
    if c.is_paused():
        print(f"Resuming '{c.name}'")
        c.resume()
        print(f"Resumed cluster '{c.name}' at {datetime.now().strftime('%H:%M:%S')} ")
    else:
        print(f"'{c.name}' is already running, nothing to do")


def pause_command(org: AtlasOrganization, arg_project_ids: List[str], arg_cluster_names: List[str]):
    for cluster_name in arg_cluster_names:
        clusters = org.get_cluster(cluster_name)
        if len(clusters) == 0:
            print(f"No such cluster '{cluster_name}'")
        elif len(clusters) == 1:
            pause_cluster(clusters[0])
        elif len(arg_project_ids) == 1:
            clusters = org.get_cluster(cluster_name, arg_project_ids[0])
            pause_cluster(clusters[0])
        elif len(arg_project_ids) < 1:
            print("You must specify only one project ID when pausing multiple clusters")
            print("You specified none (use the --project_id argument)")
        else:
            print("You must specify at least one project ID when pausing multiple clusters")
            print(f"You specified several project IDs: {arg_project_ids}")

            # pprint.pprint(result)


def resume_command(org: AtlasOrganization, arg_project_ids: List[str], arg_cluster_names: List[str]):
    for cluster_name in arg_cluster_names:
        clusters = org.get_cluster(cluster_name)
        if len(clusters) == 0:
            print(f"No such cluster '{cluster_name}'")
        elif len(clusters) == 1:
            resume_cluster(clusters[0])
        elif len(arg_project_ids) == 1:
            clusters = org.get_cluster(cluster_name, arg_project_ids[0])
            resume_cluster(clusters[0])
        elif len(arg_project_ids) < 1:
            print("You must specify only one project ID when resuming multiple clusters")
            print("You specified none (use the --project_id argument)")
        else:
            print("You must specify at least one project ID when resuming multiple clusters")
            print(f"You specified several project IDs: {arg_project_ids}")


def main():
    parser = argparse.ArgumentParser(description=
                                     f"A command line program to list organizations,"
                                     f"projects and clusters on a MongoDB Atlas organization."
                                     f"You need to enable programmatic keys for this program"
                                     f" to work. See https://docs.atlas.mongodb.com/reference/api/apiKeys/ ",
                                     epilog=f"Version: {__VERSION__}")

    parser.add_argument("--publickey", help="MongoDB Atlas public API key."
                                            "Can be read from the environment variable ATLAS_PUBLIC_KEY")
    parser.add_argument("--privatekey", help="MongoDB Atlas private API key."
                                             "Can be read from the environment variable ATLAS_PRIVATE_KEY")

    parser.add_argument("-p", "--pause", default=[], dest="pause_cluster",
                        action="append",
                        help="pause named cluster in project specified by project_id "
                             "Note that clusters that have been resumed cannot be paused "
                             "for the next 60 minutes")

    parser.add_argument("--defaultcluster", default=False, action="store_true",
                        help="Print out the default cluster we use to create clusters with the create command")

    parser.add_argument("-r", "--resume", default=[],
                        dest="resume_cluster", action="append",
                        help="resume named cluster in project specified by project_id")

    parser.add_argument("-l", "--list",
                        action="store_true",
                        default=False,
                        help="List everything in the organization")

    parser.add_argument("-lp", "--listproj",
                        action="store_true",
                        default=False,
                        help="List all projects")

    parser.add_argument("-lc", "--listcluster",
                        action="store_true",
                        default=False,
                        help="List all clusters")

    parser.add_argument("--createcluster", help="Create a cluster from the JSON file specified  as an argument")

    parser.add_argument("-o", "--output", default=None,
                        help="Specify a file for output")

    parser.add_argument("--clusterconfig", help="Name of the file used for cluster configuration with --createcluster")

    parser.add_argument("--clustername", help="Name of cluster to be created")

    parser.add_argument("-pid", "--project_id", default=[], dest="project_id_list",
                        action="append",
                        help="specify the project ID for cluster that is to be paused")

    parser.add_argument("-d", "--debug", default=False, action="store_true",
                        help="Turn on logging at debug level")

    # parser.add_argument("--http", type=HTTPOperationName, choices=list(HTTPOperationName),
    #                     help="do a http operation")
    # parser.add_argument("--url", help="URL for HTTP operation")
    # parser.add_argument("--itemsperpage", type=int, default=100,
    #                     help="No of items to return per page [default: %(default)s]")
    # parser.add_argument("--pagenum", type=int, default=1,
    #                     help="Page to return [default: %(default)s]")

    # Initializes Colorama
    init(autoreset=True)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

    logging.debug("logging is on at DEBUG level")

    # Stop noisy urllib3 info logs
    logging.getLogger("requests").setLevel(logging.WARNING)
    if args.publickey:
        public_key = args.publickey
    else:
        public_key = os.getenv("ATLAS_PUBLIC_KEY")
        if public_key is None:
            print("you must specify an ATLAS public key via --publickey arg "
                  "or the environment variable ATLAS_PUBLIC_KEY")
            sys.exit(10)

    if args.privatekey:
        private_key = args.privatekey
    else:
        private_key = os.getenv("ATLAS_PRIVATE_KEY")
        if private_key is None:
            print("you must specify an an ATLAS private key via --privatekey"
                  "arg or the environment variable ATLAS_PRIVATE_KEY")
            sys.exit(1)

    org = AtlasOrganization(public_key, private_key, populate=False)

    if args.list:
        org.pprint()

    if args.listproj:
        if args.project_id_list:
            for project_id in args.project_id_list:
                print(org.get_one_project(project_id).pretty())
        else:
            for project in org.get_projects():
                print(project.pretty())

    if args.defaultcluster:
        default_cluster = AtlasCluster.default_single_region_cluster()
        if args.output:
            with open(args.output, "w") as output_file:
                output_file.write(json.dumps(default_cluster, indent=2))
        else:
            print(AtlasCluster.pretty_dict(default_cluster))

    if args.createcluster:
        if args.clusterconfig:
            with open(args.clusterconfig, "r") as input_file:
                cfg = json.load(input_file)
            if args.clustername:
                cluster_name = args.clustername
            else:
                cluster_name = AtlasAPI.random_name()
            print(f"Creating cluster {cluster_name} from cluster configuration {args.clusterconfig}")
            org.create_cluster(cfg, cluster_name)

    if args.listcluster:
        if args.project_id_list:
            for project_id in args.project_id_list:
                if org.is_project_id(project_id):
                    for cluster in org.get_clusters(project_id):
                        print(f"\nProject: '{project_id}' Cluster: '{cluster.name}'")
                        print(cluster.pretty())
                else:
                    print(f"{project_id} is not a valid project ID")
        else:
            for project in org.get_projects():
                clusters = org.get_clusters(project.id)
                for cluster in clusters:
                    print(f"\nProject: '{project.id}' Cluster: '{cluster.name}'")
                    print(cluster.pretty())

    if args.pause_cluster or args.resume_cluster:
        if args.pause_cluster:
            pause_command(org, args.project_id_list, args.pause_cluster)
        if args.resume_cluster:
            resume_command(org, args.project_id_list, args.resume_cluster)


if __name__ == "__main__":
    try:
        main()
    except AtlasError as e:
        print(f"{Fore.RED}AtlasError:")
        print(e)
        sys.exit(1)
    except AtlasGetError as e:
        print(f"{Fore.RED}AtlasGetError:")
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"{Fore.RED}Ctrl-C...exiting")
        sys.exit(1)
