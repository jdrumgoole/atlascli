import requests
from requests.auth import HTTPDigestAuth
from atlascli.atlaskey import AtlasKey

key=AtlasKey.get_from_env()

try:
    r = requests.get("https://cloud.mongodb.com/api/atlas/v1.0/groups",
                     headers={"Accept": "application/json",
                              "Content-Type": "application/json"},
                     auth=HTTPDigestAuth(key.get_public_key, key.get_private_key))
    print(r.json())
    r.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(e)
    print(e.response)
