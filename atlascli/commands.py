from datetime import datetime
import json
import os.path

from atlascli.atlascluster import AtlasCluster
from atlascli.atlasmap import AtlasMap
from atlascli.clusterid import ClusterID

from colorama import init, Fore


class Commands:

    def __init__(self, map: AtlasMap):
        self._map = map

    @staticmethod
    def prompt(s: str, response: str) -> bool:
        reply = input(s)
        return reply.upper() == response.upper()

    def pre_flight_project_id(self, project_id:str):
        if project_id:
            if self._map.is_project_id(project_id):
                return project_id
            else:
                raise SystemExit(f"{project_id} is not a valid project ID for this organization")
        else:
            raise SystemExit(f"No project ID argument defined for this command")

    def preflight_cluster_arg(self, cluster_arg: str) -> ClusterID:
        try:
            if cluster_arg is None:
                raise SystemExit(f"command needs an argument")
            project_id, cluster_name = ClusterID.parse_cluster_name(cluster_arg)
            if project_id is None:
                project_ids = self._map.get_project_ids(cluster_name)
                if len(project_ids) == 0:
                    raise SystemExit(f"{cluster_name} is not a valid cluster name")
                elif len(project_ids) > 1:
                    raise SystemExit(f"{cluster_name} is not unique in this organization, "
                                     f"you need to specify the project id")
                else:
                    project_id = project_ids[0]
            if project_id and self._map.is_project_id(project_id):
                if cluster_name and self._map.is_cluster_name(cluster_name):
                    return ClusterID(project_id, cluster_name)
                else:
                    if cluster_name:
                        raise SystemExit(f"{cluster_name} is not a cluster name in this organization")
                    else:
                        raise SystemExit(f"No cluster name supplied as an argument")
            else:
                if project_id:
                    raise SystemExit(f"{project_id} is not a project ID in this organization")
                else:
                    raise SystemExit(f"{project_id} is not a valid project ID for this organization")
        except ValueError as e:
            raise SystemExit(e)

    def get_cluster_cmd(self, args):
        cluster_id = self.preflight_cluster_arg(args.getcluster)
        cluster = self._map.get_one_cluster(cluster_id.project_id, cluster_id.name)
        if args.output:
            with open(args.output, "w") as output_file:
                output_file.write(cluster.json())
                print(f"Cluster config created in '{Fore.MAGENTA}{args.output}{Fore.RESET}'")
        else:
            print(AtlasCluster.pretty_dict(cluster.resource))

    @staticmethod
    def default_cluster_cmd(args):
        default_cluster = AtlasCluster.default_single_region_cluster()
        if args.output:
            with open(args.output, "w") as output_file:
                output_file.write(json.dumps(default_cluster, indent=2))
                print(f"default cluster config created in '{Fore.MAGENTA}{args.output}{Fore.RESET}'")
        else:
            print(AtlasCluster.pretty_dict(default_cluster))

    def list_project_cmd(self, args):
        if args.project_id_list:
            for project_id in args.project_id_list:
                print(self._map.get_one_project(project_id).pretty(), end="")
        else:
            for project in self._map.get_projects():
                print(project.pretty(), end="")

    def create_cluster_cmd(self, args):
        project_id, cluster_name = ClusterID.parse_cluster_name(args.createcluster)
        project_id = self.pre_flight_project_id(project_id)
        if args.clusterconfig:
            if os.path.isfile(args.clusterconfig):
                with open(args.clusterconfig, "r") as input_file:
                    cfg = json.load(input_file)
                print(f"Creating cluster {Fore.YELLOW}{project_id}{Fore.RESET}:{Fore.MAGENTA}{cluster_name}"
                      f"{Fore.RESET} from cluster configuration {Fore.GREEN}{args.clusterconfig}")
                new_cluster = self._map.api.create_cluster(project_id, cluster_name, cfg)
                if args.output:
                    AtlasCluster.dump(args.output, new_cluster)
                    print(f"Cluster config created in '{Fore.MAGENTA}{args.output}{Fore.RESET}'")
                else:
                    print(new_cluster.pretty())
            else:
                raise SystemExit(f"No such file {args.clusterconfig}")
        else:
            print(f"No clusterconfig file specified with --clusterconfig")

    def list_cluster_cmd(self, args):
        for i in args.listcluster:
            cluster_id = self.preflight_cluster_arg(i) # need to handle naked cluster names
            for cluster in self._map.get_cluster(cluster_id.project_id, cluster_id.name):
                if args.output:
                    print(f"Writing {cluster_id} to {args.output}")
                    AtlasCluster.dump(args.output, cluster.resource)
                else:
                    print(f"\nProject: '{cluster_id.project_id}' Cluster: '{cluster_id.name}'")
                    print(cluster.pretty())

    @staticmethod
    def strip_cluster_cmd(args):
        if args.stripcluster:
            if os.path.isfile(args.stripcluster):
                cfg = AtlasCluster.load(args.stripcluster)
                new_cfg = AtlasCluster.strip_cluster_dict(cfg)
                if args.output:
                    AtlasCluster.dump(args.output, new_cfg)
                    print(f"Stripped config created in '{Fore.MAGENTA}{args.output}{Fore.RESET}'")
                else:
                    print(AtlasCluster.pretty_dict(new_cfg))
            else:
                raise SystemExit(f"No such file {args.stripcluster}")
        else:
            print("No argument for --stripcluster commmand")

    def delete_cluster_cmd(self, args):
        cluster_id = self.preflight_cluster_arg(args.deletecluster)
        cluster = self._map.api.get_one_cluster(cluster_id.project_id, cluster_id.name)
        print(f"deleting cluster: {cluster_id.pretty()} (project : {self._map.get_project_name(cluster.project_id)})")
        if Commands.prompt("Are you sure: ", "Y"):
            cluster = self._map.api.get_one_cluster(cluster_id.project_id, cluster_id.name)
            self._map.api.delete_cluster(cluster)
            print("delete completed")
        else:
            print("delete aborted")

    def pause_cmd(self, args):

        for cluster_name in args.pausecluster:
            cluster_id = self.preflight_cluster_arg(cluster_name)
            cluster = self._map.get_one_cluster(cluster_id.project_id, cluster_id.name)
            if cluster.is_paused():
                print(f"Cluster '{cluster.name}' is already paused")
            else:
                print(f"Trying to pause: '{cluster.name}'")
                self._map.api.pause_cluster(cluster)
                print(f"Paused cluster '{cluster.name}' at {datetime.now().strftime('%H:%M:%S')}")

    def resume_cmd(self, args):

        for cluster_name in args.resumecluster:
            cluster_id = self.preflight_cluster_arg(cluster_name)
            cluster = self._map.get_one_cluster(cluster_id.project_id, cluster_id.name)
            if cluster.is_paused():
                print(f"Trying to resume: '{cluster.name}'")
                self._map.api.resume_cluster(cluster)
                print(f"Resumed cluster '{cluster.name}' at {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"Cluster '{cluster.name}' is already running")

                # pprint.pprint(result)