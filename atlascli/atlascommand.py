from typing import Iterator

from enum import Enum
from atlascli.atlaskey import AtlasKey
from atlascli.atlasproject import AtlasProject
from atlascli.atlascluster import AtlasCluster
from atlascli.atlasorganization import AtlasOrganization


class CommandType(Enum):
    CREATE = "create"
    PATCH = "patch"
    DELETE = "delete"
    LIST = "list"
    PAUSE = "pause"
    RESUME = "resume"


class ResourceType(Enum):
    ORGANIZATION = "organization"
    PROJECT = "project"
    CLUSTER = "cluster"


class AtlasCommand:

    # def __new__(cls, atlas_key:AtlasKey=None, *args, **kwargs):
    #     cls.ATLAS_KEY = atlas_key
    #     cls.API = API(cls.ATLAS_KEY)
    #     cls._inst = super(AtlasCommand, cls).__new__(cls)
    #     return cls._inst

    def __init__(self, atlas_key:AtlasKey):
        self._atlas_key = atlas_key
        self._api = API(self._atlas_key)
        self._class = None
        self._create_func = None
        self._modify_func = None
        self._delete_func = None
        self._print_func = None

    @property
    def api(self):
        return self._api

    def id_or_name(self, atlas_resource):
        if type(atlas_resource) is AtlasCluster:
            return atlas_resource.name
        else:
            return atlas_resource.id

    def create_organization(self, name):
        return self._api.create_organization(name)

    def create(self, parent, obj):
        if self._create_func:
            self._create_func(parent, obj)
        else:
            raise NotImplemented

    def modify(self, parent, identifier, data):
        if self._modify_func:
            self._modify_func(parent, identifier, data)
        else:
            raise NotImplemented

    def delete(self, identifier):
        if self._delete_func:
            self._delete_func(identifier)
        else:
            raise NotImplemented

    def print(self, identifier):
        self._print_func(identifier)

    def print_iterator(self, resource: Iterator):
        for i in resource:
            # print(self._class)
            # print(self._executor)
            self._print_func(i)

class OrganizationCommand(AtlasCommand):

    def __init__(self, atlas_key:AtlasKey=None):
        super().__init__(atlas_key)
        self._class = AtlasOrganization
        self._create_func = api.create_organization
        self._modify_func = None
        self._delete_func = None
        self._print_func = AtlasOrganization.print

class ProjectCommand(AtlasCommand):

    def __init__(self,
                 atlas_key:AtlasKey=None):
        super().__init__(atlas_key)
        self._class = AtlasProject
        self._create_func = api.create_project
        self._modify_func = None
        self._delete_func = api.delete_project
        self._print_func = AtlasProject.print


class ClusterCommand(AtlasCommand):

    def __init__(self,
                 atlas_key:AtlasKey=None):
        super().__init__(atlas_key)
        self._class = AtlasCluster
        self._create_func = api.create_cluster
        self._modify_func = api.modify_cluster
        self._delete_func = api.delete_cluster
        self._print_func = AtlasCluster.print


class CommandFactory:

    def __init__(self, atlas_key: AtlasKey=None):
        self._atlas_key = atlas_key

    def make_command(self, cmd_type: ResourceType):
        if cmd_type is ResourceType.ORGANIZATION:
            return OrganizationCommand(self._atlas_key)
        elif cmd_type is ResourceType.PROJECT:
            return ProjectCommand(self._atlas_key)
        elif cmd_type is ResourceType.CLUSTER:
            return ClusterCommand(self._atlas_key)
        else:
            raise NotImplemented


if __name__ == "__main__":

    api = API()
    cmds = CommandFactory()
    org_cmd = cmds.make_command(ResourceType.ORGANIZATION)
    org_cmd.print_iterator(api.get_organizations())
    project_cmd = cmds.make_command(ResourceType.PROJECT)
    project_cmd.print_iterator(api.get_projects())
    cluster_cmd = cmds.make_command(ResourceType.CLUSTER)
    cluster_cmd.print_iterator(api.get_clusters_for_all_projects())
