
If you want to use the [MongoDB Atlas API](https://docs.atlas.mongodb.com/api/) 
to manage your clusters one of the first things you will discover is that 
[resource IDs](https://docs.atlas.mongodb.com/reference/api-resources/) 
are the keys to the kingdom. 

In order to use the API you will need an API key and you will need to grant 
access to your program via programmatic API keys. 

## How to create an Atlas API Key
You can create keys at the Organization level by selecting the access menu item 
on the left hand side menu:

![API Start Screen ](https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-screen.png)


Once you create a key you then need to assign it permissions. If you pick the 
default you will have to add this key explicitly to every project that you want 
to manage via the API.

![API Permissions Screen ](https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-permissions.png)

On the next screen you can collect your API key. You will only get to see it
once so please make sure to take a copy.


![API Create Key Screen ](https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-create.png)

Not on this screen we obliterate part of the key so it can't been seen. 

Finally you need to whitelist any nodes that are going to originate API requests. 

![API Create Key Screen ](https://raw.githubusercontent.com/jdrumgoole/atlasapi/master/images/api-key-whitelist.png)

You are now ready to start using your API key.

## Listing Atlas Resources

You could use the [Curl](https://curl.haxx.se/) program to query each resource
using the examples in the [API docs](https://docs.atlas.mongodb.com/api) 
but there is an easier way to do this.

First you install the python package `atlascli`. 

```shell script
$ pip install atlascli
Collecting atlascli
  Using cached https://files.pythonhosted.org/packages/32/e9/27fa8872f12b7a5ecaca1c6d3234d77eef22f68c3b89e3abf1d1af36ebe9/atlascli-0.2.6.tar.gz
Collecting requests (from atlascli)
  Using cached https://files.pythonhosted.org/packages/1a/70/1935c770cb3be6e3a8b78ced23d7e0f3b187f5cbfab4749523ed65d7c9b1/requests-2.23.0-py2.py3-none-any.whl
Requirement already satisfied: python-dateutil in c:\users\joe\appdata\roaming\python\python37\site-packages (from atlascli) (2.7.0)
Requirement already satisfied: idna<3,>=2.5 in c:\program files (x86)\microsoft visual studio\shared\python37_64\lib\site-packages (from requests->atlascli) (2.8)
Requirement already satisfied: certifi>=2017.4.17 in c:\users\joe\appdata\roaming\python\python37\site-packages (from requests->atlascli) (2019.3.9)
Requirement already satisfied: chardet<4,>=3.0.2 in c:\program files (x86)\microsoft visual studio\shared\python37_64\lib\site-packages (from requests->atlascli) (3.0.4)
Requirement already satisfied: urllib3!=1.25.0,!=1.25.1,<1.26,>=1.21.1 in c:\program files (x86)\microsoft visual studio\shared\python37_64\lib\site-packages (from requests->atlascli) (1.25.3)
Requirement already satisfied: six>=1.5 in c:\users\joe\appdata\roaming\python\python37\site-packages (from python-dateutil->atlascli) (1.12.0)
Installing collected packages: requests, atlascli
  Running setup.py install for atlascli: started
    Running setup.py install for atlascli: finished with status 'done'
Successfully installed atlascli-0.2.6 requests-2.23.0
$
```

Once this package is installed you can use the script `atlascli` to list your
resources and pause and resume specific clusters.

```shell script
$ atlascli -h
usage: atlascli [-h] [--publickey PUBLICKEY] [--privatekey PRIVATEKEY]
                [-p PAUSE_CLUSTER] [-r RESUME_CLUSTER] [-l] [-lp] [-lc]
                [-pid PROJECT_ID_LIST] [-d]

A command line program to list organizations,projects and clusters on a
MongoDB Atlas organization.You need to enable programmatic keys for this
program to work. See https://docs.atlas.mongodb.com/reference/api/apiKeys/

optional arguments:
  -h, --help            show this help message and exit
  --publickey PUBLICKEY
                        MongoDB Atlas public API key.Can be read from the
                        environment variable ATLAS_PUBLIC_KEY
  --privatekey PRIVATEKEY
                        MongoDB Atlas private API key.Can be read from the
                        environment variable ATLAS_PRIVATE_KEY
  -p PAUSE_CLUSTER, --pause PAUSE_CLUSTER
                        pause named cluster in project specified by project_id
                        Note that clusters that have been resumed cannot be
                        paused for the next 60 minutes
  -r RESUME_CLUSTER, --resume RESUME_CLUSTER
                        resume named cluster in project specified by
                        project_id
  -l, --list            List everything in the organization
  -lp, --listproj       List all projects
  -lc, --listcluster    List all clusters
  -pid PROJECT_ID_LIST, --project_id PROJECT_ID_LIST
                        specify the project ID for cluster that is to be
                        paused
  -d, --debug           Turn on logging at debug level

Version: 0.2.6

```

*For regular use we recommend using the environment variables ATLAS_PUBLIC_KEY 
and ATLAS_PRIVATE_KEY to store the API key values. That way these values will 
not leak into screen shots and log files. For the examples that follow we 
assume these environment variables have been set correctly.*

To list all the projects and clusters for the organization associated with
your API key just run `atlascli -list`.*

```shell script
$ atlascli --list
{'id': '599eeced9f78fXXXXXXXXXX',
 'links': [{'href': 'https://cloud.mongodb.com/api/atlas/v1.0/orgs/599eeced9f78fXXXXXXXXXX',
            'rel': 'self'}],
 'name': 'Open Data at MongoDB'}
Organization ID:599eeced9f78fXXXXXXXXXX Name:'Open Data at MongoDB'
     project ID:5e61578366108eXXXXXXXX Name:'Aaron'
     project ID:5dd2e441014b761XXXXXXXX Name:'Developer Relations Content Team'
       Cluster ID:'5dd2e4cecf09aXXXXXXXX' name:'Cluster0'               state=running
     project ID:57597484e4b062XXXXXXXXX Name:'MUGAlyser Project'
       Cluster ID:'581b89058a5b21XXXXXXXX' name:'MUGAlyser'              state=paused
     project ID:5a141a774e65811a132a8010 Name:'Open Data Project'
       Cluster ID:'5ae863924e658XXXXXXXX' name:'MOT'                    state=paused
       Cluster ID:'5cab57f39ccf6XXXXXXXX' name:'GDELT'                  state=paused
       Cluster ID:'5ae86bbb9701XXXXXXXXX' name:'UKPropertyPrices'       state=paused
       Cluster ID:'5ae2fb904e6XXXXXXXXXX' name:'New-York-Taxi'          state=paused
       Cluster ID:'5b9a2b39d3XXXXXXXXXXX' name:'demodata'               state=running
```



The project and org IDs have been occluded for security purposes. 
As you can see the Organization  ID, Project IDs and Cluster names are 
displayed. These will be required by other parts of the API. 

You can pause and resume an Atlas cluster using the Atlas GUI. 

![Pause a Cluster in MongoDB Atlas](https://webassets.mongodb.com/_com_assets/cms/pause_cluster-y1wtdyybzn.png)

However, when we pause a cluster the Atlas environment will restart the cluster 
after seven days. Also, both pausing and resuming require a login, 
navigation etc. Basically, it’s a drag to do this regularly. 

As long as cluster is running you are paying full price for it. When a cluster
is paused the costs drop to a fraction of the price. If you pause your cluster
from 7.00pm until 7.00am you will just about halve your cluster costs. For
development or test clusters this can amount to a lot of savings, especially if
you factor in pausing them for the whole of the weekend. 

To facilitate this activity the `atlascli` script explicitly supports `--pause` 
and `--resume` parameters. 

```shell script
$ atlascli --list
{'id': '599eeced9f78fXXXXXXXXXX',
 'links': [{'href': 'https://cloud.mongodb.com/api/atlas/v1.0/orgs/599eeced9f78fXXXXXXXXXX',
            'rel': 'self'}],
 'name': 'Open Data at MongoDB'}
Organization ID:599eeced9f78fXXXXXXXXXX Name:'Open Data at MongoDB'
     project ID:5e61578366108eXXXXXXXX Name:'Aaron'
     project ID:5dd2e441014b761XXXXXXXX Name:'Developer Relations Content Team'
       Cluster ID:'5dd2e4cecf09aXXXXXXXX' name:'Cluster0'               state=running
     project ID:57597484e4b062a0421d9bab Name:'MUGAlyser Project'
       Cluster ID:'581b89058a5b21XXXXXXXX' name:'MUGAlyser'              state=paused
     project ID:5a141a774e65811XXXXXXXXX Name:'Open Data Project'
       Cluster ID:'5ae863924e658XXXXXXXX' name:'MOT'                    state=paused
       Cluster ID:'5cab57f39ccf6XXXXXXXX' name:'GDELT'                  state=paused
       Cluster ID:'5ae86bbb9701XXXXXXXXX' name:'UKPropertyPrices'       state=paused
       Cluster ID:'5ae2fb904e6XXXXXXXXXX' name:'New-York-Taxi'          state=paused
       Cluster ID:'5b9a2b39d3XXXXXXXXXXX' name:'demodata'               state=running
```


To get the project ID look for the **project ID** field. To get the cluster 
name just look for **name** field on the **CLuster ID** line. 

Now to pause the cluster just run:

```shell script
$ atlascli --project_id 5a141a774e65811XXXXXXXXX --pause demodata
Pausing 'demodata'
Paused cluster 'demodata'

$
$
```

To resume a cluster just use the `--resume` argument instead of the `--pause` 
argument. 

Want to pause or resume more than one cluster in a single project? You can, 
just by adding multiple --pause or --resume arguments. 

```shell script
$ atlascli --project_id 5a141a774e65811XXXXXXXXX --resume demodata --resume GDELT
Resuming cluster 'demodata'
Resumed cluster 'demodata'
Resuming cluster 'GDELT'
Resumed cluster 'GDELT'
```

One final thing. Once you have resumed a cluster you can't pause it again for
at least an hour. This is to give the maintainance scripts a change to audit and
update your cluster if required. 

Now, you just need to add this script to your favourite scheduler to save
yourself a ton of money.
