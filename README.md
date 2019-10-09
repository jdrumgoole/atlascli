# MongoDB Atlas - A Python API for MongoDB Atlas

The MongoDB database as a service offering [Atlas](https://www.mongodb.com/cloud/atlas) provides
a complete and well documented [REST API](https://docs.atlas.mongodb.com/api/).

## Installation

The easiest way to install the `mongodbatlas` is with `pip`.

```shell
$ pip install mongodbatlas
```

Once the installation completes you can confirm it has worked by running

```shell
$ atlascli -h
usage: atlascli [-h] [--publickey PUBLICKEY] [--privatekey PRIVATEKEY] [--org]
                [--pause PAUSE_CLUSTER] [--resume RESUME_CLUSTER]
                [--list {projects,clusters}] [--cluster CLUSTER]
                [--project_id PROJECT_DETAIL] [--format {summary,full}]
                [--debug] [--resource RESOURCE] [--itemsperpage ITEMSPERPAGE]
                [--pagenum PAGENUM]

optional arguments:
  -h, --help            show this help message and exit
  --publickey PUBLICKEY
                        MongoDB Atlas public API key
  --privatekey PRIVATEKEY
                        MongoDB Atlas private API key
...
```


The Python Atlas API wraps the REST API in a more Pythonic
API based around an ``AtlasAPI`` class. 

The library assumes the existence of two environment variables:

* `ATLAS_PUBLIC_KEY` : The public key value defined by the 
[Atlas programmatic API key](https://docs.atlas.mongodb.com/configure-api-access/#programmatic-api-keys)
* `ATLAS_PRIVATE_KEY` : The private key defined by the Atlas programmatic API
key.

## How to create an Atlas API Key
You can create keys at the Organization level by selecting the access menu item 
on the left hand side menu:

![API Start Screen ](https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-screen.png)


Once you create a key you then need to assign it permissions. If you pick the 
default youwill have to add this key explicitly to every project that you want 
to manage via the API.

![API Permissions Screen ](https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-permissions.png)

On the next screen you can collect your API key. You will only get to see it
once so please make sure to take a copy.


![API Create Key Screen ](https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-create.png)

Not on this screen we obliterate part of the key so it can't been seen. 

Finally you need to whitelist any nodes that are going to originate API requests. 

![API Create Key Screen ](https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-whitelist.png)

You are now ready to start using your API key.

## Using your keys

Both parts of the key required to acc
