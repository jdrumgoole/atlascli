import pprint
import random
import string
import json
from datetime import datetime
from dateutil import parser
from typing import Dict

from colorama import Fore

from atlascli.outputformat import OutputFormat
from pygments import highlight
from pygments.styles import default, colorful, emacs, get_style_by_name
from pygments.lexers import JsonLexer
from pygments.formatters import Terminal256Formatter


def json_datetime_encoder(item: datetime):
    return str(item)


class AtlasResource:
    """
    Base class for Atlas Resources
    """

    CLUSTER_NAME_CHARS = string.ascii_letters + string.digits + '-'
    # Valid characters in an Atlas cluster name

    def __init__(self, resource: Dict = None):
        if resource:
            self._resource = resource
            if "created" in self._resource:  # convert date string to datetime obj
                self._resource["created"] = parser.parse(self._resource["created"])
        else:
            self._resource = {}

    def __eq__(self, rhs):
        """Overrides the default implementation"""
        if isinstance(rhs, AtlasResource):
            return self.resource == rhs.resource
        return NotImplemented

    @property
    def id(self):
        return self._resource["id"]

    @property
    def resource(self) -> Dict:
        return self._resource

    @property
    def name(self) -> str :
        return self._resource["name"]

    @name.setter
    def name(self, new_name: str):
        self._resource["name"] = new_name

    @property
    def resource(self) -> Dict:
        return self._resource

    def __setitem__(self, key, value):
        self._resource[key] = value
    
    def __getitem__(self, key):
        return self._resource[key]

    def __delitem__(self, key):
        del self._resource[key]

    @resource.setter
    def resource(self, item: Dict):
        self._resource = item

    def json(self, indent=2):
        return json.dumps(self._resource, indent=indent, default=json_datetime_encoder)

    @staticmethod
    def iter_print(iter, func, format):
        for i in iter:
            func(i).print_resource(format)

    def pprint(self, fmt=OutputFormat.SUMMARY):
        if fmt is OutputFormat.SUMMARY:
            print(self.summary())
        elif fmt is OutputFormat.PYTHON:
            pprint.pprint(self._resource, indent=2)
        elif fmt is OutputFormat.JSON:
            print(self.json())

    @classmethod
    def pretty_dict(cls, d: Dict) -> str:
        return highlight(json.dumps(d, indent=2, default=json_datetime_encoder), JsonLexer(),
                         Terminal256Formatter(style=get_style_by_name('emacs')))

    def pretty(self) -> str:
        return AtlasResource.pretty_dict(self._resource)

    @staticmethod
    def dump(output_filename: str, d: Dict):
        with open(output_filename, "w") as output_file:
            output_file.write(json.dumps(d, indent=2))

    @staticmethod
    def load(input_filename: str):
        with open(input_filename, "r") as input_file:
            return json.load(input_file)

    # def __call__(self):
    #     return self._resource

    @staticmethod
    def is_valid_cluster_name(s: str) -> bool:
        for c in s:
            if c not in AtlasResource.CLUSTER_NAME_CHARS:
                return False
        return True

    def pretty_id(self):
        return f"{Fore.CYAN}{self.id}{Fore.RESET}"

    def pretty_name(self):
        return f"{Fore.GREEN}{self.name}{Fore.RESET}"

    def pretty_id_name(self):
        return f"{self.pretty_id()}:{self.pretty_name()}"

    def __str__(self):
        return f"{pprint.pformat(self._resource)}"

    def __repr__(self):
        res = f"{pprint.pformat(self._resource, width=40)}"
        return f"{self.__class__.__name__}(resource={res})"
