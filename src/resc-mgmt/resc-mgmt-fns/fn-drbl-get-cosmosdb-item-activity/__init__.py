import json
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
# from azure.cosmos.partition_key import PartitionKey
import logging
import os
from collections import namedtuple
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

def main(requestId) -> str:

    logging.info('Starting execution of the activity function')   
    host = os.environ['COSMOS_DB_ACCOUNT_HOST']
    master_key = os.environ['COSMOS_DB_ACCOUNT_MASTER_KEY']
    database_id = os.environ['COSMOS_DB_DATABASE_ID']
    container_id = os.environ['COSMOS_DB_CONTAINER_ID']

    if (host and master_key and database_id and container_id):
        try: 
            # cred = DefaultAzureCredential()
            client = cosmos_client.CosmosClient(host, {'masterKey': master_key}, 
                        user_agent="AzureResourceManager", user_agent_overwrite=True)
            db_client = client.get_database_client(database_id)
            container_client = db_client.get_container_client(container_id)            
            response = container_client.read_item(requestId) 
            return response
        except Exception as e:
            logging.exception(e)
            return str(e)
    else:
        return 'One or more required environment settings are missing'
