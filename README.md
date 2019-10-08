# Altas API - A Python API for MongoDB Atlas

The MongoDB database as a service offering [Atlas](https://www.mongodb.com/cloud/atlas) provides
a complete and well documented [REST API](https://docs.atlas.mongodb.com/api/).

The Python Atlas API wraps the REST API in a more Pythonic
API based around an ``AtlasAPI`` class. 

The library assumes the existence of two environment variables:

* `ATLAS_PUBLIC_KEY` : The public key value defined by the 
[Atlas programmatic API key](https://docs.atlas.mongodb.com/configure-api-access/#programmatic-api-keys)
* `ATLAS_PRIVATE_KEY` : The private key defined by the Atlas programmatic API
key.

You can create keys on this screen:

API Screen: https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-screen.png "API Screen" 

These keys can be generated by using the Access tab on MongoDB Atlas at the
Organization level.


