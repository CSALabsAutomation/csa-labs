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
        # authorityinline = "https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47"
        # client_id = "740557c5-aaa2-4104-84a7-dbf7b5f35861"
        # scope = ["https://graph.microsoft.com/.default"]
        # secret = "U6g8Q~yqKXZwyUaPpGsGm-XlpMl3N0YLgiqzVbhk"
        # app = msal.ConfidentialClientApplication(client_id,authority=authorityinline,client_credential=secret)
        # result = None
        # result = app.acquire_token_silent(scope,account=None)

        # if not result:
        #  logging.info("No suitable token exists in cache")
        #  result = app.acquire_token_for_client(scopes=scope)

        # if "access_token" in result:
        #  token = result["access_token"]
        #  logging.info(token)
        # else:
        #  token = DefaultAzureCredential().get_token('https://graph.microsoft.com/.default').token
        token = DefaultAzureCredential().get_token('https://graph.microsoft.com/.default').token
        user_list = []
        for upn in params['upnList']:
                user_list += listUsers(upn, token)
        return user_list
    except Exception as e:
        logging.exception(e)
        return str(e)      
