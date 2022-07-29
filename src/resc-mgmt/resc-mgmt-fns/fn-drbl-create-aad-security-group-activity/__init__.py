import json
import requests
import logging
from azure.identity import DefaultAzureCredential

def main(params):
    logging.info('Starting execution function')   
       
    try: 
        url = 'https://graph.microsoft.com/v1.0/groups'
        token = DefaultAzureCredential().get_token('https://graph.microsoft.com/.default').token
        headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {token}"}
        body = {
            "displayName": params['groupName'],
            "mailNickname": params['groupName'],
            "description": params['groupDesc'],
            "securityEnabled": True,
            "mailEnabled": False,
            "groupTypes": []
        }
        response = requests.post(url, data=json.dumps(body), headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.exception(e)
        return str(e)

        