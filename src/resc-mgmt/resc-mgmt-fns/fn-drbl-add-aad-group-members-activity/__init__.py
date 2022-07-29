import json
import requests
import logging
import azure.functions as func
from azure.identity import DefaultAzureCredential

def getMemberList(member_id_list):
    member_list = []
    for id in member_id_list:
        member_list.append(f"https://graph.microsoft.com/v1.0/directoryObjects/{id}")
    return member_list

def main(params):
    logging.info('Starting execution function')   

    try: 
        token = DefaultAzureCredential().get_token('https://graph.microsoft.com/.default').token
        url = f"https://graph.microsoft.com/v1.0/groups/{params['groupId']}"
        headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {token}"}
        body = {
            "members@odata.bind": getMemberList(params['memberIdList'])
        }            
        response = requests.patch(url, data=json.dumps(body), headers=headers)
        response.raise_for_status()
        return "Ok"    
    except Exception as e:
        logging.exception(e)
        return str(e)      
