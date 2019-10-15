import pprint
import random
import string
import json
from datetime import datetime
from dateutil import parser

from mongodbatlas.atlaskey import AtlasKey
from mongodbatlas.apimixin import APIMixin, OutputFormat


def json_datetime_encoder(item:datetime):
    return str(item)


class AtlasResource(APIMixin):
    """
    Base class for Atlas Resources
    """

    def __init__(self, resource=None, api_key:AtlasKey=None):
        super().__init__(api_key=api_key)
        if resource:
            self._resource = resource
            if "created" in self._resource:  # convert date string to datetime obj
                self._resource["created"] = parser.parse(self._resource["created"])
        else:
            self._resource = {}

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def id(self):
        return self._resource["id"]

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

    def summary_string(self):
        return f"id:'{self.id}' name:'{self.name}'"

    def print_resource(self, fmt=OutputFormat.SUMMARY):
        if fmt is OutputFormat.SUMMARY:
            print(self.summary_string())
        elif fmt is OutputFormat.PYTHON:
            pprint.pprint(self._resource, indent=2)
        elif fmt is OutputFormat.JSON:
            print(json.dumps(self._resource, indent=2, default=json_datetime_encoder))

    # def __call__(self):
    #     return self._resource

    def get_ids(self, field):
        for i in self.get_resource_by_item(f"/{field}"):
            yield i["id"]

    def get_names(self, field):
        for i in self.get_resource_by_item(f"/{field}"):
            yield i["name"]

    @staticmethod
    def random_name():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    def __str__(self):
        return f'{pprint.pformat(self._resource)}'

    def __repr__(self):
        return f"{self.__class__.__name__}({self._resource!r})"
