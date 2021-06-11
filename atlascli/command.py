
from enum import Enum
from atlascli.atlasapi import AtlasAPI
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


class Command:

    API=None
    ATLAS_KEY=None

    def __new__(cls, atlas_key:AtlasKey=None, *args, **kwargs):
        cls.ATLAS_KEY = atlas_key
        cls.API = AtlasAPI()
        cls._inst = super(Command, cls).__new__(cls)
        return cls._inst

    def __init__(self, command:CommandType=None):
        self._command_type = command

    @property
    def command_type(self):
        return self._command_type

    def __call__(self, *args):
        pass


class ListCommand(Command):

    def __init__(self,
                 atlas_key:AtlasKey=None):
        self._command_type = CommandType.LIST
        super().__init__(atlas_key)
        self._class = None
        self._executor = None

    def command_type(self):
        return self._command_type

    def __call__(self, resources:tuple):
        if self._class is None :
            raise NotImplemented
        for i in resources:
            self._class.print_resource(self._executor(i.id))


class ListOrganizationCommand(ListCommand):

    def __init__(self, atlas_key: AtlasKey = None):
        super().__init__(atlas_key)
        self._resource_type = ResourceType.ORGANIZATION
        self._command_type = (CommandType.LIST, self._resource_type)
        self._class = AtlasOrganization
        self._executor = AtlasAPI.get_one_organization


class ListProjectCommand(Command):

    def __init__(self, atlas_key:AtlasKey=None):
        super().__init__(atlas_key)
        self._resource_type = ResourceType.PROJECT
        self._command_type = ( CommandType.LIST, self._resource_type)
        self._class = AtlasProject
        self._executor = AtlasAPI.get_one_project


class ListClusterCommand(ListCommand):

    def __init__(self, atlas_key: AtlasKey = None):
        super().__init__(atlas_key)
        self._resource_type = ResourceType.PROJECT
        self._command_type = (CommandType.LIST, ResourceType.CLUSTER)
        self._executor = AtlasAPI.get_one_cluster
        self._class = AtlasCluster

if __name__ == "__main__":
    list_cmd = ListOrganizationCommand()
    list_cmd(list(ListOrganizationCommand.API.get_organizations()))
    # print(type(cmd.api.get_organizations()))
    # for i in cmd.api.get_organizations():
    #     print(i)
