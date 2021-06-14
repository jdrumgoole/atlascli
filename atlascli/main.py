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

from colorama import init, Fore

from atlascli.atlaskey import AtlasKey

from atlascli.errors import AtlasError, AtlasGetError
from atlascli.atlasapi import AtlasAPI
from atlascli.version import __VERSION__

from atlascli.atlasmap import AtlasMap
from atlascli.commands import Commands


def main():

    parser = argparse.ArgumentParser(description=
                                     f"A command line program to list organizations,"
                                     f"projects and clusters on a MongoDB Atlas organization."
                                     f"You need to enable programmatic keys for this program"
                                     f" to work. See https://docs.atlas.mongodb.com/reference/api/apiKeys/ ",
                                     epilog=f"Version: {__VERSION__}")

    subparsers = parser.add_subparsers(dest="subparser_name")

    listprojects_parser = subparsers.add_parser('listprojects', aliases=["lp"])

    listprojects_parser.add_argument('-pid', '--project_ids', nargs="*",
                                     help="List of project IDs to output")

    listprojects_parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='UTF-8'))

    pause_parser = subparsers.add_parser('pause')

    pause_parser.add_argument('-c', '--cluster_ids', nargs="*",
                              help="List of Cluster IDs to pause")

    resume_parser = subparsers.add_parser('resume')

    resume_parser.add_argument('-c', '--cluster_ids', nargs="*",
                               help="List of Cluster IDs to resume")

    parser.add_argument("--listall", default=False, action="store_true")

    list_parser = subparsers.add_parser('list')

    list_parser.add_argument('-c', '--cluster_names', nargs="*",
                               help="List of Cluster names to print")

    list_parser.add_argument('-p', '--project_ids', nargs="*",
                               help="List of Cluster IDs to print")

    list_parser.add_argument('-org', '--organization', default=False, action="store_true",
                             help="print out the organization")

    list_parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='UTF-8'))

    parser.add_argument("--publickey", help="MongoDB Atlas public API key."
                                            "Can be read from the environment variable ATLAS_PUBLIC_KEY")
    parser.add_argument("--privatekey", help="MongoDB Atlas private API key."
                                             "Can be read from the environment variable ATLAS_PRIVATE_KEY")

    parser.add_argument("--defaultcluster", default=False, action="store_true",
                        help="Print out the default cluster we use to create clusters with the create command")

    parser.add_argument("-p", "--pausecluster", default=[],
                        action="append",
                        help="pause named cluster in project specified by <project_id>:<cluster_name>"
                             "if the cluster name is unique that is all that is required e.g. -p <cluster_name>"
                             "Not that clusters that have been resumed cannot be paused for 60 minutes")

    parser.add_argument("-r", "--resumecluster", default=[],
                        action="append",
                        help="resume named cluster in project specified by <project_id>:<cluster_name>"
                             "if the cluster name is unique that is all that is required e.g. -r <cluster_name>")

    parser.add_argument("-lc", "--listcluster",
                        action="append",
                        default=[],
                        help="List all clusters in the organization")

    parser.add_argument("--getcluster", help="Get the configuration for a specific cluster")

    parser.add_argument("--deletecluster", help="Delete cluster defined in arg")

    parser.add_argument("--createcluster", help="Create a cluster from the JSON file specified  as an argument")

    # parser.add_argument("-o", "--output", default=None,
    #                     help="Specify a file for output")

    parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='UTF-8'))

    parser.add_argument("--clusterconfig", help="Name of the file used for cluster configuration with --createcluster")

    parser.add_argument("--stripcluster", help="Take a JSON file containing a cluster config and strip out fields"
                                               "that cannot be used to create a cluster from the config")


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

    if args.listall:
        atlas_map.pprint()

    if args.subparser_name == "listprojects":
        print(args.project_ids, args.output)
        commands.list_project_cmd(args.project_ids, args.output)

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

    if args.deletecluster:
        commands.delete_cluster_cmd(args)

    if args.subparser_name == "pause" :
        commands.pause_cmd(args.cluster_ids)

    if args.subparser_name == "resume":
        commands.resume_cmd(args.cluster_ids)

    if args.subparser_name == "list":
        print(args.cluster_names)
        if args.cluster_names is not None and (len(args.cluster_names) == 0):
            cluster_names = list(atlas_map.get_cluster_names())
        else:
            cluster_names = args.cluster_names
        commands.list_cmd(args.organization, args.project_ids, cluster_names, args.output)


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
