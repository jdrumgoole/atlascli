import pytest
from mongodb_atlas_api import MongoDBAtlasAPI


def test_get_orgs():

    api = MongoDBAtlasAPI()
    orgs = api.get_orgs()
    for i in orgs:
        print(i)
