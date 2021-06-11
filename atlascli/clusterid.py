from __future__ import annotations

import string

from colorama import init, Fore

from atlascli.atlasresource import AtlasResource


class ProjectID:

    def __init__(self, id:str, throw_exception: bool = True):
        self._id = ProjectID.validate_project_id(id, throw_exception)

    @property
    def id(self):
        return self._id

    @staticmethod
    def validate_project_id(p: str, throw_exception: bool = True) -> str:
        if p is None:
            raise ValueError("project_id cannot be None")
        if len(p) < 24:
            if throw_exception:
                raise ValueError(f"Not a valid project ID, project ID cannot be less than 24 chars: '{p}'")
            else:
                return None
        elif len(p) > 24:
            if throw_exception:
                raise ValueError(f"Not a valid project ID, project ID cannot be more than 24 chars: '{p}'")
            else:
                return None

        for c in p:
            if c not in string.hexdigits:
                if throw_exception:
                    raise ValueError(f"Not valid project ID, string is not hexadecimal: '{p}'")
                else:
                    return None
        return p

    def __eq__(self, rhs):
        return self.id == rhs.id

    def __str__(self):
        return f"{self.id}"

class ClusterID:

    def __init__(self, project_id: str, cluster_name: str, throw_exception: bool = True):

        self._project_id = ProjectID.validate_project_id(project_id, throw_exception)
        self._name = ClusterID.validate_cluster_name(cluster_name, throw_exception)

    @property
    def project_id(self):
        return self._project_id

    @property
    def name(self):
        return self._name

    @staticmethod
    def validate_cluster_name(c: str, throw_exception=True) -> str:
        if AtlasResource.is_valid_cluster_name(c):
            return c
        else:
            if throw_exception:
                raise ValueError(f"Not a valid cluster ID, only a-zA-Z, 0-9 and '-' are allowed")
            else:
                return None

    @staticmethod
    def parse(s: str) -> ClusterID:
        project_id, separator, cluster_name = s.partition(":")

        return ClusterID(ProjectID.validate_project_id(project_id),
                         ClusterID.validate_cluster_name(cluster_name))

    @staticmethod
    def parse_cluster_name(cluster_name: str) -> (str, str):
        id, sep, name = cluster_name.partition(":")
        if len(sep) == 0:
            return None, id
        elif len(id) == 0:
            return None, name
        else:
            return id, name

        raise ValueError(f"{cluster_name} cannot be parsed as a cluster name of the form 'id:name'")

    def __eq__(self, rhs):
        return (self.project_id == rhs.project_id) and (self.name == rhs.name)

    def __str__(self):
        return f"{self.project_id}:{self._name}"

    def __repr__(self):
        return f"{__name__}(project_id={self._project_id}, cluster_name={self._name})"

    def pretty(self):
        return f"{Fore.YELLOW}{self.project_id}:{Fore.GREEN}{self.name}{Fore.RESET}"
