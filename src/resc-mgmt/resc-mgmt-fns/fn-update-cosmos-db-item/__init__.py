import json
import logging
import os
from collections import namedtuple
from urllib import response
import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.identity import DefaultAzureCredential

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Starting execution function')   
    
    try: 
        host = os.environ['COSMOS_DB_ACCOUNT_HOST']
        master_key = os.environ['COSMOS_DB_ACCOUNT_MASTER_KEY']
        database_id = os.environ['COSMOS_DB_DATABASE_ID']
        container_id = os.environ['COSMOS_DB_CONTAINER_ID']
    except KeyError: 
        return func.HttpResponse('Missing one or more required environment settings', status_code = 400)

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse('Invalid request body', status_code = 400)
    else:
        query = req_body.get('query')
        extendedconsumption = req_body.get('extendedconsumption')
        extensionapprovedDateTime = req_body.get('extensionapprovedDateTime')
        extensionrequestedDateTime = req_body.get('extensionrequestedDateTime')
        ownerName = req_body.get('ownerName')
        ownerEmail = req_body.get('ownerEmail')
        extendedDescription = req_body.get('extendedDescription')
   
    if (query and extendedconsumption and extensionapprovedDateTime and extensionrequestedDateTime and ownerName and ownerEmail):
        try: 
            # cred = DefaultAzureCredential()
            client = cosmos_client.CosmosClient(host, {'masterKey': master_key}, 
                        user_agent="AzureResourceManager", user_agent_overwrite=True)
            db_client = client.get_database_client(database_id)
            container_client = db_client.get_container_client(container_id)            
            oneitem = list(container_client.query_items(query=query, enable_cross_partition_query=True))
            #oneitem = container_client.read_item(items['id'], partition_key=items['resourceGroupName'])
            oneitem[0]['approvedconsumption'] = int(oneitem[0]['approvedconsumption']) + int(extendedconsumption)
            oneitem[0]['lastrequestinitiatedDateTime'] = extensionrequestedDateTime
            oneitem[0]['lastrequestapprovedDateTime'] = extensionapprovedDateTime
            oneitem[0]['ownerName'] = ownerName
            oneitem[0]['ownerEmail'] = ownerEmail
            oneitem[0]['description'] = extendedDescription
            updateoneitem = container_client.upsert_item(body=oneitem[0])
            response = list(container_client.query_items(query=query, enable_cross_partition_query=True))
            return func.HttpResponse(json.dumps(response), status_code = 200)
        except exceptions.CosmosResourceNotFoundError:
            return func.HttpResponse("Request not found", status_code=404)
        except Exception as e:
            logging.exception(e)
            return func.HttpResponse(str(e), status_code=500)
    else:
        return func.HttpResponse('Missing one or more required parameters', status_code = 400)        
