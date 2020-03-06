# MongoDB Atlas - A Python API for MongoDB Atlas

The MongoDB database as a service offering [Atlas](https://www.mongodb.com/cloud/atlas) provides
a complete and well documented [REST API](https://docs.atlas.mongodb.com/api/).

## Installation

The easiest way to install the `mongodbatlas` is with `pip`.

```shell
C:\Users\joe>pip install mongodbatlas
Looking in indexes: https://test.pypi.org/simple/
Processing c:\users\joe\appdata\local\pip\cache\wheels\6c\2f\e8\7f33b6b37b40424f1d00d54048aaa63fd47c7b289e790a997d\mongodbatlas-0.2.5b5-py3-none-any.whl
Requirement already satisfied: python-dateutil in c:\users\joe\.virtualenvs\joe-93pxapbd\lib\site-packages (from mongodbatlas) (2.8.1)
Requirement already satisfied: requests in c:\users\joe\.virtualenvs\joe-93pxapbd\lib\site-packages (from mongodbatlas) (2.5.4.1)
Requirement already satisfied: six>=1.5 in c:\users\joe\.virtualenvs\joe-93pxapbd\lib\site-packages (from python-dateutil->mongodbatlas) (1.10.0)
Installing collected packages: mongodbatlas
Successfully installed mongodbatlas-0.2.5b

C:\Users\joe>
```

Once the installation completes you can confirm it has worked by running

```shell
C:\Users\joe>atlascli -h
usage: atlascli [-h] [--publickey PUBLICKEY] [--privatekey PRIVATEKEY]
                [--pause PAUSE_CLUSTER] [--resume RESUME_CLUSTER] [--list]
                [--listproj] [--listcluster] [--cluster CLUSTER]
                [--project_id PROJECT_ID_LIST] [--debug]

A command line program to list organizations,projects and clusters on a
MongoDB Atlas organization.

optional arguments:
  -h, --help            show this help message and exit
  --publickey PUBLICKEY
                        MongoDB Atlas public API key
  --privatekey PRIVATEKEY
                        MongoDB Atlas private API key
  --pause PAUSE_CLUSTER
                        pause named cluster in project specified by project_id
                        Note that clusters that have been resumed cannot be
                        pausedfor the next 60 minutes
  --resume RESUME_CLUSTER
                        resume named cluster in project specified by
                        project_id
  --list                List everything in the organization
  --listproj            List all projects
  --listcluster         List all clusters
  --cluster CLUSTER     list all elements for for project_id:cluster_name
  --project_id PROJECT_ID_LIST
                        specify project for cluster that is to be paused
  --debug               Turn on logging at debug level

Version: 0.2.5b5

C:\Users\joe>
```


The Python Atlas API wraps the REST API in a more Pythonic
API based around an ``AtlasAPI`` class. 

The library assumes the existence of two environment variables:

* `ATLAS_PUBLIC_KEY` : The public key value defined by the 
[Atlas programmatic API key](https://docs.atlas.mongodb.com/configure-api-access/#programmatic-api-keys)
* `ATLAS_PRIVATE_KEY` : The private key defined by the Atlas programmatic API
key.

These can be passed in on the command line as well as parameters 
`--publickey` and `--privatekey`.

See the section [below](#how-to-create-an-atlas-api-key) on how to create a programmatic Atlas API key.

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

Both parts of the key required to access your account. Rather than passing them 
in on the command line the `atlascli` program these can read them from the environment
variables `ATLAS_PRIVATE_KEY` and `ATLAS_PUBLIC_KEY`. 
