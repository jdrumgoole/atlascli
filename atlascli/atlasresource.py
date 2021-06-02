import pprint
import random
import string
import json
from datetime import datetime
from dateutil import parser
from typing import Dict

from atlascli.outputformat import OutputFormat
from atlascli.atlasapi import AtlasAPI
from pygments import highlight
from pygments.styles import default, colorful, emacs, get_style_by_name
from pygments.lexers import JsonLexer
from pygments.formatters import Terminal256Formatter

def json_datetime_encoder(item:datetime):
    return str(item)


class AtlasResource:
    """
    Base class for Atlas Resources
    """

    def __init__(self, api:AtlasAPI=None, resource:Dict=None):
        if resource:
            self._resource = resource
            if "created" in self._resource:  # convert date string to datetime obj
                self._resource["created"] = parser.parse(self._resource["created"])
        else:
            self._resource = {}

        if api:
            self._api = api
        else:
            self._api = AtlasAPI()

    @property
    def api(self):
        return self._api
    @property
    def timestamp(self):
        return self._timestamp

    @property
    def id(self):
        return self._resource["id"]

    @property
    def resource(self):
        return self._resource

    @property
    def name(self):
        return self._resource["name"]

    @name.setter
    def name(self, new_name):
        self._resource["name"] = new_name

    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, item):
        self._resource = item

    @staticmethod
    def iter_print(iter, func, format):
        for i in iter:
            func(i).print_resource(format)

    def pprint(self, fmt=OutputFormat.SUMMARY):
        if fmt is OutputFormat.SUMMARY:
            print(self.summary_string())
        elif fmt is OutputFormat.PYTHON:
            pprint.pprint(self._resource, indent=2)
        elif fmt is OutputFormat.JSON:
            print(json.dumps(self._resource, indent=2, default=json_datetime_encoder))

    @classmethod
    def pretty_dict(cls, d:Dict)->str:
        return highlight(json.dumps(d, indent=2, default=json_datetime_encoder), JsonLexer(), Terminal256Formatter(style=get_style_by_name('emacs')))

    def pretty(self)->str:
        return AtlasResource.pretty_dict(self._resource)

    # def __call__(self):
    #     return self._resource




    def __str__(self):
        return f"{pprint.pformat(self._resource)}"

    def __repr__(self):
        res=f"{pprint.pformat(self._resource, width=40)}"
        return f"{self.__class__.__name__}(resource={res})"
