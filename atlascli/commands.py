from datetime import datetime
import json
import os.path
from typing import List

from atlascli.atlascluster import AtlasCluster
from atlascli.atlasmap import AtlasMap
from atlascli.atlasresource import AtlasResource, inputhighlight
from atlascli.clusterid import ClusterID

from colorama import init, Fore
import click


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
                raise SystemExit(f"{inputhighlight(project_id)} is not a valid project ID for this organization")
        else:
            raise SystemExit(f"No project ID argument defined for this command")

    def preflight_cluster_arg(self, cluster_arg: str) -> ClusterID:
        try:
            if cluster_arg is None:
                raise SystemExit(f"command needs an argument")
            project_id, cluster_name = ClusterID.parse_id_name(cluster_arg)
            if project_id is None:
                project_ids = self._map.get_cluster_project_ids(cluster_name)
                if len(project_ids) == 0:
                    raise SystemExit(f"{inputhighlight(cluster_name)} is not a valid cluster name in this organization")
                elif len(project_ids) > 1:
                    raise SystemExit(f"{inputhighlight(cluster_name)} is not unique in this organization, "
                                     f"you need to specify the project id")
                else:
                    project_id = project_ids[0]
            if project_id and self._map.is_project_id(project_id):
                if cluster_name and self._map.is_cluster_name(cluster_name):
                    return ClusterID(project_id, cluster_name)
                else:
                    if cluster_name:
                        raise SystemExit(f"{inputhighlight(cluster_name)} is not a cluster name in this organization")
                    else:
                        raise SystemExit(f"No cluster name supplied as an argument")
            else:
                if project_id:
                    raise SystemExit(f"{inputhighlight(project_id)} is not a project ID in this organization")
                else:
                    raise SystemExit(f"{inputhighlight(project_id)} is not a valid project ID for this organization")
        except ValueError as e:
            raise SystemExit(e)

    @staticmethod
    def default_cluster_cmd(output_file=None):
        default_cluster = AtlasCluster.default_single_region_cluster()
        if output_file:
            output_file.write(json.dumps(default_cluster, indent=2))
            print(f"default cluster config created in {inputhighlight(output_file.name)}")
        else:
            print(AtlasCluster.pretty_dict(default_cluster))

    def create_cluster_cmd(self, cluster_name: str, cfg_file, output_file=None):
        project_id, cluster_name = ClusterID.parse_id_name(cluster_name)
        if cfg_file:
            cfg_dict = json.load(cfg_file)
            print(f"Creating cluster {Fore.YELLOW}{project_id}{Fore.RESET}:{Fore.MAGENTA}{cluster_name}"
                  f"{Fore.RESET} from cluster configuration {Fore.GREEN}{cfg_file.name}")
            new_cluster = self._map.api.create_cluster(project_id, cluster_name, cfg_dict)
            if output_file:
                json.dump(output_file, new_cluster)
                print(f"Cluster config created in '{Fore.MAGENTA}{output_file.name}{Fore.RESET}'")
            else:
                print(new_cluster.pretty())

    def create_project_cmd(self, project_name:str, output_file=None):
        print(f"Creating project {self._map.org_id}:{project_name}")
        project = self._map.api.create_project(self._map.org_id, project_name)
        if output_file:
            json.dump(output_file, project)
            print(f"Cluster config created in '{Fore.MAGENTA}{output_file.name}{Fore.RESET}'")
        else:
            print(project.pretty())

    @staticmethod
    def template_cluster_cmd(cfg_file, output_file=None):
        cfg = json.load(cfg_file)
        new_cfg = AtlasCluster.strip_cluster_dict(cfg)
        if output_file:
            output_file.write(json.dumps(new_cfg))
            print(f"Template config created in '{Fore.MAGENTA}{output_file.name}{Fore.RESET}'")
        else:
            print(AtlasCluster.pretty_dict(new_cfg))

    def clone_cluster_cmd(self, cluster_name: str, output_file=None):
        cluster_id = self.preflight_cluster_arg(cluster_name)
        cluster = self._map.get_one_cluster(cluster_id.project_id, cluster_id.name)
        new_cfg = AtlasCluster.strip_cluster_dict(cluster.resource)
        if output_file:
            output_file.write(json.dumps(new_cfg))
            print(f"Cloned cluster {cluster.pretty_id_name()} into {Fore.LIGHTWHITE_EX}{output_file.name}")
        else:
            print(AtlasResource.pretty_dict(new_cfg))

    def delete_cluster_cmd(self, cluster_name: str):
        cluster_id = self.preflight_cluster_arg(cluster_name)
        print(f"deleting cluster: {cluster_id.pretty()} (project : {self._map.get_project_name(cluster_id.project_id)})")
        if Commands.prompt("Are you sure: ", "Y"):
            cluster = self._map.api.get_one_cluster(cluster_id.project_id, cluster_id.name)
            self._map.api.delete_cluster(cluster)
            print("delete completed")
        else:
            print("delete aborted")

    def delete_project_cmd(self, project_name: str):
        print(f"deleting project: {Fore.LIGHTWHITE_EX}{project_name}{Fore.RESET} (project ID : {self._map.get_project_id(project_name)})")
        if Commands.prompt("Are you sure: ", "Y"):
            project = self._map.api.get_one_project(self._map.get_project_id(project_name))
            self._map.api.delete_project(project.id)
            print("delete completed")
        else:
            print("delete aborted")

    def list_projects(self, projects: List[str], output = None):
        if projects is None or len(projects) == 0:
            project_ids = self._map.get_project_ids()
        else:
            project_ids = projects

        for pid in project_ids:
            if self._map.is_project_id(pid):
                project = self._map.get_one_project(pid)
                if output:
                    output.write(project.json())
                    print(f"wrote project {project.summary()} to {output.name}")
                else:
                    print(project.pretty(), end="")
            else:
                print(f"{pid} is not a valid project_id in this organization")

    def list_cluster(self, cluster_names: List[str], output=None):
        for i in cluster_names:
            cluster_id = self.preflight_cluster_arg(i)  # need to handle naked cluster names
            for cluster in self._map.get_cluster(cluster_id.name, cluster_id.project_id):
                if output:
                    print(f"Writing {cluster_id} to {output.name}")
                    output.write(cluster.json())
                else:
                    print(f"\nProject: '{cluster_id.project_id}' Cluster: '{cluster_id.name}'")
                    print(cluster.pretty())

    @click.command()
    @click.option("--name", type=str, default="Bongo")
    def list(self, name):
        click.echo(f"name: {name}")
        
    def list_cmd(self, org:bool, project_ids : List[str], cluster_names: List[str], output=None):
        if not org and not project_ids and not cluster_names:
            self._map.pprint()
        else:
            if org:
                print(AtlasResource.pretty_dict(self._map.organization.resource))
            if project_ids:
                self.list_projects(project_ids, output)
            if cluster_names:
                self.list_cluster(cluster_names, output)

    def pause_cmd(self, cluster_names: List[str]):

        for cluster_name in cluster_names:
            cluster_id = self.preflight_cluster_arg(cluster_name)
            cluster = self._map.get_one_cluster(cluster_id.project_id, cluster_id.name)
            if cluster.is_paused():
                print(f"Cluster '{cluster.name}' is already paused")
            else:
                print(f"Trying to pause: '{cluster.name}'")
                self._map.api.pause_cluster(cluster)
                print(f"Paused cluster '{cluster.name}' at {datetime.now().strftime('%H:%M:%S')}")

    def resume_cmd(self, cluster_ids: List[str]):

        for cluster_name in cluster_ids:
            cluster_id = self.preflight_cluster_arg(cluster_name)
            cluster = self._map.get_one_cluster(cluster_id.project_id, cluster_id.name)
            if cluster.is_paused():
                print(f"Trying to resume: '{cluster.name}'")
                self._map.api.resume_cluster(cluster)
                print(f"Resumed cluster '{cluster.name}' at {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"Cluster '{cluster.name}' is already running")
