import requests
import argparse
from datetime import datetime

key = "b3n2jUTEtEnxn0bYeVKJ9GINcQuhooxmcHdfCXOBsTwt1LVFmbR3xd0I4rhEFR4h"
data_api = "https://data.mongodb-api.com/app/data-idfwi/endpoint/data/beta"

insertOne_api = f"{data_api}/action/insertOne"


def insert_one(doc):
    result = requests.post(url=insertOne_api,
                           headers={'Content-Type': 'application/json',
                                    'Access-Control-Request-Headers': '*',
                                    'api-key': f'{key}',
                                    },
                           payload={
                               "dataSource": "demodata",
                               "database": "learn-data-api",
                               "collection": "test",
                               "document": doc,
                           }
                           )


# parser = argparse.ArgumentParser()
#
# parser.add_argument("-i", "--insert", type=dict)
# args = parser.parse_args()

insert_one({"hello" : datetime.datetime.utcnow()})



# print(args.find)
