import logging
from collections import namedtuple
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import *
from azure.identity import DefaultAzureCredential

Params = namedtuple('Params', ['subscriptionId', 'query'])

def main(params: Params) -> str:
    logging.info('Starting execution of activity function')   
    subscription_id, query = params    
    if (subscription_id and query):
        try: 
            cred = DefaultAzureCredential()
            resourcegraph_client = ResourceGraphClient(
                credential=cred,
                subscription_id=subscription_id
            )
            query = QueryRequest(
                    query=query,
                    subscriptions=[subscription_id])
            query_response = resourcegraph_client.resources(query)
            return { "data": query_response.data }
        except Exception as e:
            logging.exception(e)
            return str(e)
    else:
        return 'One or more required parameters are missing'
