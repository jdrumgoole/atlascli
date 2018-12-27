import pytest

from atlasapi.atlasorganization import AtlasOrganizationAPI, AtlasProjectAPI,\
    AtlasClusterAPI


def test_atlas_organization():

    api = AtlasOrganizationAPI()
    org = api.get_organization("5c23d4d2f2a30b921dd5dd9d")
    assert org is not None
    assert org.id == "5c23d4d2f2a30b921dd5dd9d"


def test_atlas_projects():

    api = AtlasProjectAPI()
    project = api.get_project("5c242f12553855347ce303af")
    assert project is not None
    assert project.id == "5c242f12553855347ce303af"


def test_atlas_clusters():

    api = AtlasClusterAPI()
    cluster = api.get_cluster("5c242f12553855347ce303af", "Cluster0")
    assert cluster is not None
    assert cluster.name == "Cluster0"
