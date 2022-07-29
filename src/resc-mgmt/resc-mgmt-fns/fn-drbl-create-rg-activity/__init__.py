import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

def main(params) -> dict:
    logging.info('Starting execution of the activity function')   
    try: 
        cred = DefaultAzureCredential() 
        resource_client = ResourceManagementClient(cred, params['subscriptionId'])
        result = resource_client.resource_groups.create_or_update(
                params['resourceGroupName'],
                {
                    "location": params['location'],
                    "tags": { "RequestType":params['requestType'], "MsxEngagementId": params['msxEngagementId'] }
                }
            )
        return { 
            "id": result.id, 
            "name": result.name,
            "location": result.location,
            "tags": result.tags 
        }
    except Exception as e:
        logging.exception(e)
        return str(e)