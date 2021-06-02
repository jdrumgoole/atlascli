import pprint

from colorama import Fore
from atlascli.atlasresource import AtlasResource


class AtlasProject(AtlasResource):

    def __init__(self, api, project:dict=None):
        super().__init__(api, project)

    def summary(self):
        return f"{Fore.MAGENTA}project ID{Fore.RESET}: {self.id} {Fore.MAGENTA}Name{Fore.RESET}: {Fore.YELLOW}'{self.name}'"

    def __str__(self):
        return f"{pprint.pformat(self._resource)}"





