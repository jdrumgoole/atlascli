

from atlasapi.atlasorganization import AtlasOrganizationAPI, AtlasProjectAPI,\
    AtlasClusterAPI


def test_atlas_organization():

    api = AtlasOrganizationAPI()
    org = api.get_organization("5c23d4d2f2a30b921dd5dd9d")
    assert org is not None
    assert org.id == "5c23d4d2f2a30b921dd5dd9d"


def test_atlas_organisations():

    # Not working

    api = AtlasOrganizationAPI()
    orgs = api.get_organisations()
    assert orgs is not None
    assert list(orgs) is not None
    assert len(list(orgs)) > 0


def test_atlas_project():

    api = AtlasProjectAPI()
    project = api.get_project("5c242f12553855347ce303af")
    assert project is not None
    assert project.id == "5c242f12553855347ce303af"


def test_atlas_projects():

    api = AtlasProjectAPI()
    projects = api.get_projects("5c23d4d2f2a30b921dd5dd9d")
    assert projects is not None
    assert list(projects) is not None
    assert len(list(projects)) >= 0


def test_atlas_cluster():

    api = AtlasClusterAPI()
    cluster = api.get_cluster("5c242f12553855347ce303af", "Cluster0")
    assert cluster is not None
    assert cluster.name == "Cluster0"

def test_atlas_clusters():

    # broken

    api = AtlasClusterAPI()
    clusters = api.get_clusters("5c242f12553855347ce303af")
    assert clusters is not None
    assert list(clusters) is not None
    assert len(list(clusters)) >= 0
