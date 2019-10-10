"""
Basic Python API to MongoDB Atlas Services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@Author:Joe.Drumgoole@mongodb.com

"""
import os
import pprint
import logging
from logging import StreamHandler

from requests.auth import HTTPDigestAuth
import requests

from .atlaskey import AtlasKey
from .errors import AtlasGetError, \
                    AtlasPatchError, \
                    AtlasPostError, \
                    AtlasAuthenticationError,\
                    AtlasEnvironmentError,\
                    AtlasInitialisationError


class APIMixin(object):
    """
    Basic API class for accessing MongoDB Atlas Assets

    Also note that the terms projects and groups are used interchangeably
    between the API and the UI and are synonyms.
    """

    SITE_URL="https://cloud.mongodb.com"
    API_URL = f"/api/atlas/v1.0"
    ATLAS_BASE_URL=f"{SITE_URL}{API_URL}"

    ATLAS_HEADERS = {"Accept": "application/json",
                     "Content-Type": "application/json"}

    def __init__(self,
                 api_key:AtlasKey=None,
                 page_size=100,
                 debug=0):

        self._api_key: AtlasKey = api_key
        self._auth = None
        self._debug = None
        self._log = logging.getLogger(__name__)
        self._page_size = page_size

        if self._page_size < 1 or self._page_size > 500 :
            raise AtlasInitialisationError("'page_size' must be between 1 and 500")


        if api_key:
            self._api_key = api_key
        else:
            self._api_key = AtlasKey.get_from_env()

        if debug:
            self._debug = debug
        else:
            atlas_debug_env = os.getenv("ATLAS_DEBUG", 0)
            try:
                self._debug = int(atlas_debug_env)
            except ValueError:
                raise AtlasEnvironmentError(f"Invalid value for ATLAS_DEBUG env: '{atlas_debug_env}'")

        if self._debug:
            self._log = logging.getLogger(__name__)

        # print(self._username)
        # print(self._api_key)
        self._auth = HTTPDigestAuth(self._api_key.public_key, self._api_key.private_key)

    @property
    def api_key(self):
        return self._api_key

    def post(self, resource, data):
        self._log.debug(f"post({resource}, {data})")

        try:
            #print(f"atlas_post:{resource}, {data}")
            r = requests.post(resource, data=data, headers=self.ATLAS_HEADERS, auth=self._auth)
            #print(r.url)
            r.raise_for_status()
            if self._log:
                self._log.debug(f"returns:")
                self._log.debug(f"\n{pprint.pprint(r.json())}")

        except requests.exceptions.HTTPError as e:
            raise AtlasPostError(e)
        return r.json()

    def get(self, resource, headers=None, page_num=1, items_per_page=100):
        self._log.debug(f"get({resource})")
        # Need to use the raw URL when getting linked data

        assert self._api_key is not None
        assert self._api_key != ""

        args =""
        if "itemsPerPage" not in resource:
            args=args+f"?itemsPerPage={items_per_page}"

        if "pageNum" not in resource:
            if len(args) > 0 :
                args = args + "&"
            args=args+f"pageNum={page_num}"

        resource = resource + "/" + args

        try:
            r = requests.get(resource,
                             headers=headers,
                             auth=self._auth)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise AtlasGetError(e, r.json()["detail"])
        return r.json()

    def atlas_post(self, resource, data):
        return self.post(f"{self.ATLAS_BASE_URL}{resource}", data)

    def atlas_get(self,resource=None, page_num=1, items_per_page=100):
        if resource is None:
            resource = ""
        return self.get(f"{self.ATLAS_BASE_URL}{resource}", items_per_page=items_per_page, page_num=page_num)

    def atlas_patch(self, resource, data):
        self._log.debug(f"atlas_patch({resource}, {data})")
        return self.patch(f"{self.ATLAS_BASE_URL}{resource}", data)

    def patch(self, resource, patch_doc):
        try:
            p = requests.patch(f"{resource}",
                               json=patch_doc,
                               headers=self.ATLAS_HEADERS,
                               auth=self._auth
                               )
            p.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(patch_doc)
            raise AtlasPatchError(e, p.json()["detail"])
        return p.json()

        return p.json()

    def get_text(self, resource):
        return self.get(resource).text

    def get_resource_by_page(self, resource):
        """
        return each array of resources as a single
        :param resource:
        :return:
        """
        self._log.debug(f"get_resource_by_page({resource})")
        results = None
        next_link = None

        doc = self.atlas_get(resource)

        if 'results' in doc:
            results = doc["results"]
        else:
            raise AtlasGetError(f"No 'results' field in '{doc}'")

        links = doc['links']
        last_link = links[-1]
        # print(links)
        # print(last_link)
        if "rel" in last_link and "next" == last_link["rel"]:
            next_link = last_link["href"]
        else:
            next_link = None

        return results, next_link

    def _get_results(self, doc):
        if 'results' in doc:
            for i in doc["results"]:
                yield i
        else:
            raise AtlasGetError(f"No 'results' field in '{doc}'")


class APIFormatter(object):

    def __init__(self, api):
        self._api = api
        self._spacing = 24

    @staticmethod
    def quote(s):
        return f"'{s}'"

    @staticmethod
    def print_cluster_summary_header():
        print("{:24} {:24} {:24}{:4}".format("Organisation", "Project", "Cluster", "Paused/Running"))

    @staticmethod
    def print_cluster_summary(org=None, project=None, cluster=None, paused=None, sep=" "):

        summary = f"{org:24}{sep}{project:24}{sep}{cluster:24}"

        if cluster:
            if paused:
                summary += "{:4}".format("P")
            else:
                summary += "{:4}".format("R")

        print(summary)

    def print_org_summary(self, org, ids=None):
        # print_atlas(f"Org:{org['id']}")
        projects = self._api.get_projects(org["id"])
        for project_count, project in enumerate(projects, 1):
            # print_atlas(f"Project:{project['id']}")
            try:
                clusters = self._api.get_clusters(project["id"])
            except requests.exceptions.HTTPError as e:
                pprint.pprint(e)
                continue
            for cluster_count, cluster in enumerate(clusters, 1):
                try:
                    if ids:
                        self.print_cluster_summary(org['id'],
                                                   project["id"],
                                                   cluster["name"],
                                                   cluster["paused"],
                                                   sep=":")
                    else:
                        self.print_cluster_summary(org["name"],
                                                   project["name"],
                                                   cluster["name"],
                                                   cluster["paused"],
                                                   sep=" ")

                except requests.exceptions.HTTPError as e:
                    pprint.pprint(e)
                    continue
