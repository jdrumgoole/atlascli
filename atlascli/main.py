#!/usr/bin/env python3

"""
MongoDB Atlas API (atlascli)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python API to MongoDB Atlas.

create:
    stateName : Creating
Pause to resume:
    stateName : REPAIRING

Resume to pause:
    stateName: REPAIRING

Resume to delete:
    stateName: DELETING

Paused or Resumed
    stateName : IDLE


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
from atlascli.clusterid import ClusterID
from atlascli.errors import AtlasError, AtlasGetError
from atlascli.atlasapi import AtlasAPI
from atlascli.version import __VERSION__
from atlascli.atlasorganization import AtlasOrganization
from atlascli.atlascluster import AtlasCluster
from atlascli.atlasmap import AtlasMap
from atlascli.commands import Commands


# def pause_cluster(m:AtlasMap, c: AtlasCluster):
#     if c.is_paused():
#         print(f"Cluster '{c.name}' is already paused")
#     else:
#         print(f"Trying to pause: '{c.name}'")
#         m.api.pause_cluster(c)
#         print(f"Paused cluster '{c.name}' at {datetime.now().strftime('%H:%M:%S')}")
#
#
# def resume_cluster(m: AtlasMap, c: AtlasCluster):
#     if c.is_paused():
#         print(f"Resuming '{c.name}'")
#         m.api.resume_cluster(c)
#         print(f"Resumed cluster '{c.name}' at {datetime.now().strftime('%H:%M:%S')} ")
#     else:
#         print(f"'{c.name}' is already running, nothing to do")
#
#
# def pause_command(m: AtlasMap, arg_project_ids: List[str], arg_cluster_names: List[str]):
#     for cluster_name in arg_cluster_names:
#         clusters = m.get_cluster(cluster_name)
#         if len(clusters) == 0:
#             print(f"No such cluster '{cluster_name}'")
#         elif len(clusters) == 1:
#             pause_cluster(m, clusters[0])
#         elif len(arg_project_ids) == 1:
#             clusters = m.get_cluster(cluster_name, arg_project_ids[0])
#             pause_cluster(m, clusters[0])
#         elif len(arg_project_ids) < 1:
#             print("You must specify only one project ID when pausing multiple clusters")
#             print("You specified none (use the --project_id argument)")
#         else:
#             print("You must specify at least one project ID when pausing multiple clusters")
#             print(f"You specified several project IDs: {arg_project_ids}")
#
#             # pprint.pprint(result)
#
#
# def resume_command(m: AtlasMap, arg_project_ids: List[str], arg_cluster_names: List[str]):
#     for cluster_name in arg_cluster_names:
#         clusters = m.get_cluster(cluster_name)
#         if len(clusters) == 0:
#             print(f"No such cluster '{cluster_name}'")
#         elif len(clusters) == 1:
#             resume_cluster(m, clusters[0])
#         elif len(arg_project_ids) == 1:
#             clusters = m.get_cluster(cluster_name, arg_project_ids[0])
#             resume_cluster(m, clusters[0])
#         elif len(arg_project_ids) < 1:
#             print("You must specify only one project ID when resuming multiple clusters")
#             print("You specified none (use the --project_id argument)")
#         else:
#             print("You must specify at least one project ID when resuming multiple clusters")
#             print(f"You specified several project IDs: {arg_project_ids}")

#
# def magenta(s: str) -> str:
#     return f"{Fore.MAGENTA}{s}{Fore.RESET}"


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

    parser.add_argument("-p", "--pausecluster", default=[],
                        action="append",
                        help="pause named cluster in project specified by project_id "
                             "Note that clusters that have been resumed cannot be paused "
                             "for the next 60 minutes")

    parser.add_argument("--defaultcluster", default=False, action="store_true",
                        help="Print out the default cluster we use to create clusters with the create command")

    parser.add_argument("-r", "--resumecluster", default=[],
                        action="append",
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
                        action="append",
                        default=[],
                        help="List all clusters")

    parser.add_argument("--getcluster", help="Get the configuration for a specific cluster")

    parser.add_argument("--deletecluster", help="Delete cluster defined in arg")

    parser.add_argument("--createcluster", help="Create a cluster from the JSON file specified  as an argument")

    parser.add_argument("-o", "--output", default=None,
                        help="Specify a file for output")

    parser.add_argument("--clusterconfig", help="Name of the file used for cluster configuration with --createcluster")

    parser.add_argument("--stripcluster", help="Take a JSON file containing a cluster config and strip out fields"
                                               "that cannot be used to create a cluster from the config")
    parser.add_argument("--clustername", help="Name of cluster to be created")

    # parser.add_argument("-pid", "--project_id", default=[], dest="project_id_list",
    #                     action="append",
    #                     help="specify the project ID for cluster that is to be paused")

    parser.add_argument("-d", "--debug", default=False, action="store_true",
                        help="Turn on logging at debug level")

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
            raise SystemExit("you must specify an ATLAS public key via --publickey arg "
                             "or the environment variable ATLAS_PUBLIC_KEY")

    if args.privatekey:
        private_key = args.privatekey
    else:
        private_key = os.getenv("ATLAS_PRIVATE_KEY")
        if private_key is None:
            raise SystemExit("you must specify an an ATLAS private key via --privatekey"
                             "arg or the environment variable ATLAS_PRIVATE_KEY")

    api = AtlasAPI()
    org = None
    api.authenticate(AtlasKey(public_key, private_key))
    try:
        org = api.get_this_organization()
    except AtlasError:
        raise SystemExit("Your keys may be invalid.  Please check the values for "
                         "ATLAS_PRIVATE_KEY and ATLAS_PUBLIC_KEY")

    atlas_map = AtlasMap(org, api)
    commands = Commands(atlas_map)
    if args.list:
        atlas_map.pprint()

    if args.listproj:
        commands.list_project_cmd(args)

    if args.getcluster:
        commands.get_cluster_cmd(args)

    if args.defaultcluster:
        commands.default_cluster_cmd(args)

    if args.createcluster:
        commands.create_cluster_cmd(args)

    if args.stripcluster:
        commands.strip_cluster_cmd(args)
    if args.listcluster:
        commands.list_cluster_cmd(args)
        # if args.project_id_list:
        #     for project_id in args.project_id_list:
        #         if atlas_map.is_project_id(project_id):
        #             for cluster in atlas_map.get_clusters(project_id):
        #                 print(f"\nProject: '{project_id}' Cluster: '{cluster.name}'")
        #                 print(cluster.pretty())
        #         else:
        #             print(f"{project_id} is not a valid project ID")
        # else:
        #     for project in atlas_map.get_projects():
        #         clusters = atlas_map.get_clusters(project.id)
        #         for cluster in clusters:
        #             print(f"\nProject: '{project.id}' Cluster: '{cluster.name}'")
        #             print(cluster.pretty())

    if args.deletecluster:
        commands.delete_cluster_cmd(args)

    if args.pausecluster:
        commands.pause_cmd(args)

    if args.resumecluster:
        commands.resume_cmd(args)


if __name__ == "__main__":
    try:
        main()
    except AtlasError as e:
        print(f"{Fore.RED}AtlasError:")
        print(e)
        raise
        # print("Have you set ATLAS_PRIVATE_KEY and ATLAS_PUBLIC_KEY? You can pass keys on the command line with")
        # print("--publickey and --privatekey")
        sys.exit(1)
    except AtlasGetError as e:
        print(f"{Fore.RED}AtlasGetError:")
        print(e)
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"{Fore.RED}Ctrl-C...exiting")
        sys.exit(1)
