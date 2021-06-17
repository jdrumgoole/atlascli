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

from atlascli.atlascluster import AtlasCluster
from atlascli.atlaskey import AtlasKey
from atlascli.clusterid import ClusterID, ProjectID

from atlascli.errors import AtlasError, AtlasGetError
from atlascli.atlasapi import AtlasAPI
from atlascli.version import __VERSION__

from atlascli.atlasmap import AtlasMap
from atlascli.commands import Commands


def main(argv : list[str] = None):

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

    # parser.add_argument("--defaultcluster", default=False, action="store_true",
    #                     help="Print out the default cluster we use to create clusters with the create command")

    subparsers = parser.add_subparsers(dest="subparser_name")

    default_parser = subparsers.add_parser(name="defaultcluster", help="Create a default cluster in JSON")

    default_parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='UTF-8'),
                                 help="Write the default cluster to this file")

    clone_parser = subparsers.add_parser("clone")

    clone_parser.add_argument("-c", "--cluster_name", type=ClusterID.validate_cluster_name, help="Clone this cluster")

    clone_parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='UTF-8'),
                              help="Write the cloned cluster to this file")

    pause_parser = subparsers.add_parser('pause', help="Pause a cluster")

    pause_parser.add_argument('-c', '--cluster_name', type=ClusterID.validate_cluster_name, nargs="*",
                              help="List of Cluster names to pause")

    resume_parser = subparsers.add_parser('resume', help="Resume a cluster")

    resume_parser.add_argument('-c', '--cluster_name', type=ClusterID.validate_cluster_name, nargs="*",
                               help="List of Cluster names to resume")

    list_parser = subparsers.add_parser('list', help="List organizations, projects and/or clusters")

    list_parser.add_argument('-c', '--cluster_name', type=ClusterID.validate_cluster_name, nargs="*",
                             help="List of Cluster names to print")

    list_parser.add_argument('-p', '--project_id', type=ProjectID.canonical_project_id, nargs="*",
                               help="List of project IDs to print")

    list_parser.add_argument('-org', '--organization', default=False, action="store_true",
                             help="print out the organization")

    list_parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='UTF-8'),
                             help="Send the output of this list command to a file")

    create_parser = subparsers.add_parser('create', help="Create a cluster")

    create_parser.add_argument("-c", "--cluster_name", type=ClusterID.canonical_name,
                               help="specify the name of the cluster as <project_id>:<cluster_name>")

    create_parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='UTF-8'),
                               help="Write the created cluster config to this file")

    create_parser.add_argument("-j", "--jsonconfig", type=argparse.FileType("r", encoding='UTF-8'),
                               help="Specify a JSON file we can use to create a cluster")

    delete_parser = subparsers.add_parser("delete", help="Delete a cluster")
    
    delete_parser.add_argument("-c", "--cluster_name", type=ClusterID.canonical_name,
                               help="Delete cluster defined in arg")

    parser.add_argument("--stripcluster", help="Take a JSON file containing a cluster config and strip out fields"
                                               "that cannot be used to create a cluster from the config")

    parser.add_argument("-d", "--debug", default=False, action="store_true",
                        help="Turn on logging at debug level")

    # Initializes Colorama
    init(autoreset=True)

    # if len(argv) == 1:
    #     parser.print_help(sys.stderr)
    #     return

    args = parser.parse_args(argv)

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
            raise SystemExit("you must specify an an ATLAS private key via --privatekey "
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

    if args.subparser_name == "clone":
        commands.clone_cluster_cmd(args.cluster_name, args.output)

    if args.subparser_name == "defaultcluster":
        commands.default_cluster_cmd(args.output)

    if args.subparser_name == "create":
        commands.create_cluster_cmd(args.cluster_name, args.jsonconfig, args.output)

    if args.stripcluster:
        commands.strip_cluster_cmd(args)

    if args.subparser_name == "delete":
        commands.delete_cluster_cmd(args.cluster_name)

    if args.subparser_name == "pause" :
        commands.pause_cmd(args.cluster_name)

    if args.subparser_name == "resume":
        commands.resume_cmd(args.cluster_name)

    if args.subparser_name == "list":

        if args.cluster_name is not None and (len(args.cluster_name) == 0):
            cluster_names = list(atlas_map.get_cluster_names())
        else:
            cluster_names = args.cluster_name
        if args.project_id is not None and (len(args.project_id) == 0):
            project_ids = list(atlas_map.get_project_ids())
        else:
            project_ids = args.project_id
        commands.list_cmd(args.organization, project_ids, cluster_names, args.output)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
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
