
import pytest

from atlasapi.api import AtlasAPI
from atlasapi.atlaskey import AtlasKey
from atlasapi.errors import AtlasInitialisationError

def test_atlaskey():

    keys = AtlasKey("aaaaa", "bbbbb")
    print(keys)

def test_atlas_organization():

    api = AtlasAPI()
    org = api.get_organization("599eeced9f78f769464d175c")
    assert org is not None
    assert org.id == "599eeced9f78f769464d175c"


def test_atlas_organisations():

    api = AtlasAPI()
    orgs = api.get_organisations(limi=200)
    list_of_orgs = list(orgs)
    assert list_of_orgs is not None
    assert len(list_of_orgs) == 200

    with pytest.raises(AtlasInitialisationError):
        api = AtlasAPI(page_size=0)

    with pytest.raises(AtlasInitialisationError):
        api = AtlasAPI(page_size=501)

    with pytest.raises(AtlasInitialisationError):
        api = AtlasAPI(page_size=-1)


def test_atlas_project():

    api = AtlasAPI()
    project = api.get_project("5a141a774e65811a132a8010")
    assert project is not None
    assert project.id == "5a141a774e65811a132a8010"


def test_atlas_projects():

    api = AtlasAPI()
    projects = api.get_projects("5a141a774e65811a132a8010")
    assert projects is not None
    assert list(projects) is not None
    assert len(list(projects)) >= 0


def test_atlas_cluster():

    api = AtlasAPI()
    cluster = api.get_cluster("5a141a774e65811a132a8010", "Foodapedia")
    assert cluster is not None
    assert cluster.name == "Foodapedia"


def test_atlas_clusters():

    api = AtlasAPI()
    clusters = api.get_clusters("5a141a774e65811a132a8010")
    assert clusters is not None
    assert list(clusters) is not None
    assert len(list(clusters)) >= 0
