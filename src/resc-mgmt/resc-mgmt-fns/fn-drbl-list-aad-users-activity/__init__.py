import json
import requests
import logging
import msal
import azure.functions as func
from azure.identity import DefaultAzureCredential

def listUsers(upn, token): 
    url = f"https://graph.microsoft.com/v1.0/users?$filter=startswith(userPrincipalName, '{upn}')"        
    headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['value']

def main(params):
    logging.info('Starting execution function')   

    try: 
        token = DefaultAzureCredential().get_token('https://graph.microsoft.com/.default').token
        user_list = []
        for upn in params['upnList']:
                user_list += listUsers(upn, token)
        return user_list
    except Exception as e:
        logging.exception(e)
        return str(e)      
