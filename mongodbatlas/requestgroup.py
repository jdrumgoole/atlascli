import requests
from requests.auth import HTTPDigestAuth
from mongodbatlas.atlaskey import AtlasKey

key=AtlasKey.get_from_env()

try:
    r = requests.get("https://cloud.mongodb.com/api/atlas/v1.0/groups",
                     headers={"Accept": "application/json",
                              "Content-Type": "application/json"},
                     auth=HTTPDigestAuth(key.public_key, key.private_key))
    print(r.json()["detail"])
    r.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response)
