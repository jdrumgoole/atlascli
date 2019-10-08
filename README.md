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

![API Start Screen ](https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-screen.png)


Note you have to be at the organisation level.

Once you create a key pay attention to the next screen. If you pick the default you
will have to add this key explicitly to every project that you want to manage via
the API.

![API Permissions Screen ](https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-permissions.png)

On the next screen you can collect your API key. You will only get to see it
once so please make sure to take a copy.


![API Create Key Screen ](https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-create.png)



