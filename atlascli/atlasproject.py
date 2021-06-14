import pprint
from typing import Dict

from colorama import Fore
from atlascli.atlasresource import AtlasResource


class AtlasProject(AtlasResource):

    def __init__(self, project: Dict = None):
        super().__init__(project)

    def pretty_name(self):
        return f"{Fore.YELLOW}{self.name}{Fore.RESET}"

    def __str__(self):
        return f"{pprint.pformat(self._resource)}"





