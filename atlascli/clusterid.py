from __future__ import annotations

import string

from colorama import init, Fore

from atlascli.atlasresource import AtlasResource


class ProjectID:

    def __init__(self, id: str, throw_exception: bool = True):
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
                    raise ValueError(f"Not a valid project ID, string is not hexadecimal: '{p}'")
                else:
                    return None
        return p

    @staticmethod
    def canonical_project_id(pid: str) -> str:
        try:
            return ProjectID.validate_project_id(pid, throw_exception=True)

        except ValueError as e:
            print(e)
            raise

    def __eq__(self, rhs):
        return self.id == rhs.id

    def __str__(self):
        return f"{self.id}"


class ClusterID:

    CLUSTER_NAME_CHARS = string.ascii_letters + string.digits + '-'
    # Valid characters in an Atlas cluster name

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
    def validate_cluster_name(cluster_name: str, throw_exception=True) -> str:
        for c in cluster_name:
            if c not in ClusterID.CLUSTER_NAME_CHARS:
                if throw_exception:
                    print(f"{Fore.RED}{cluster_name}{Fore.RESET} is not a valid cluster "
                          f"(ASCII letters, numbers and '-' only")
                    raise ValueError("{cluster_name} is not a valid cluster (ASCII letters, numbers and '-' only")
                else:
                    return None
        return cluster_name

    @staticmethod
    def parse(s: str) -> ClusterID:
        project_id, separator, cluster_name = s.partition(":")

        return ClusterID(ProjectID.validate_project_id(project_id),
                         ClusterID.validate_cluster_name(cluster_name))

    @staticmethod
    def parse_id_name(cluster_name: str) -> (str, str):
        id, sep, name = cluster_name.partition(":")
        if len(sep) == 0:
            return None, id
        elif len(id) == 0:
            return None, name
        else:
            return id, name

        raise ValueError(f"{cluster_name} cannot be parsed as a cluster name of the form 'id:name'")

    @staticmethod
    def canonical_name(cluster_name: str) -> str:
        #
        # check that the cluster name is of the form
        # <project_id>:<cluster-name> Used by argparse. The name
        # is tuned to fit the error message
        #
        project_id, sep, name = cluster_name.partition(":")
        if len(sep) == 0:
            print(f"{cluster_name} must have a project ID and a cluster name seperated by a ':'")
            raise ValueError

        try:
            project_id = ProjectID.validate_project_id(project_id, throw_exception=True)
            name = ClusterID.validate_cluster_name(name, throw_exception=True)
        except ValueError as e:
            print(e)
            raise

        return f"{project_id}:{name}"

    def __eq__(self, rhs):
        return (self.project_id == rhs.project_id) and (self.name == rhs.name)

    def __str__(self):
        return f"{self.project_id}:{self._name}"

    def __repr__(self):
        return f"{__name__}(project_id={self._project_id}, cluster_name={self._name})"

    def pretty(self):
        return f"{Fore.YELLOW}{self.project_id}:{Fore.GREEN}{self.name}{Fore.RESET}"
