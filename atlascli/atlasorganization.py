from typing import List, Dict, Generator

from colorama import Fore

import pprint

from atlascli.atlasresource import AtlasResource


class AtlasOrganization(AtlasResource):

    def __init__(self, org:Dict = None):

        super().__init__(org)

    def summary(self) -> str:
        return f"Organization ID: {self.pretty_project_id()}"

    def __str__(self):
        return f"{pprint.pformat(self._resource)}"


