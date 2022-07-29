import json
import requests
import logging
import azure.functions as func
from azure.identity import DefaultAzureCredential

def main(params):
    logging.info('Starting execution function')   

    try: 
        url = f"https://graph.microsoft.com/v1.0/groups/{params['groupId']}/owners/$ref"
        token = DefaultAzureCredential().get_token('https://graph.microsoft.com/.default').token
        headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {token}"}
        body = {
            "@odata.id": f"https://graph.microsoft.com/v1.0/users/{params['ownerId']}"                
        }
        response = requests.post(url, data=json.dumps(body), headers=headers)
        response.raise_for_status()
        return "Ok"
    except Exception as e:
        logging.exception(e)
        return str(e)      
