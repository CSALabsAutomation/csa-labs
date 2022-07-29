import logging
import json
import os
from datetime import datetime
import time 
import azure.durable_functions as df

# def getRequestId():    
#     # return uuid.uuid4().hex[:6]   


def getUserIds(teamEmails):
    if (teamEmails):
        emailList = teamEmails.split(';')
        userIdList = []
        for email in emailList:
            x = email.split('@')            
            userIdList.append(x[0])
        return list(set(userIdList))
    else:
        return []

def getAadUserObjectIds(aadUsersList):
    if (aadUsersList):
        userAadObjectIds = []
        for user in aadUsersList:
            userAadObjectIds.append(user['id'])
        return userAadObjectIds
    else:
        return []     


def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info("Starting execution of orchastrator function")

    #Get parameters from input
    params = context.get_input()    
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    
    if ('requestType' in params):
        if(params['requestType'].lower() == 'poc'):
            if not 'msxEngagementId' in params:
                return 'MSX Engagement Id is mandtory for POC'
            if not 'client' in params:
                return 'Client is mandtory for POC'
            msx_engmt_id = params['msxEngagementId']
            client = params['client']
            request_type = params['requestType']
        else:
            msx_engmt_id = params['msxEngagementId']
            client = params['client']        
            request_type = params['requestType']
    else: 
        request_type = 'demo'
        msx_engmt_id = 'NA'
        client = 'NA'

    if ('resourceGroupName' in params):
        rg_name = params['resourceGroupName']
    else: 
        rg_name = f"az-{request_type}-{params['requestId']}-rg"    
    
    if ('location' in params):
        location = params['location']
    else: 
        location = "centralus"
    
    
    get_aad_owner_result = yield context.call_activity('fn-drbl-list-aad-users-activity', { 'upnList': [ f"{params['ownerEmail']}"] })    
    if (get_aad_owner_result):
        owner = get_aad_owner_result[0]
    # logging.warning(owner)

    userIdList = getUserIds(params['teamEmails'])
    # logging.warning(userIdList)
    if (userIdList):
        get_aad_users_result = yield context.call_activity('fn-drbl-list-aad-users-activity', { 'upnList': userIdList } )
        # logging.warning(get_aad_users_result[0])
    else: 
        get_aad_users_result = None
    
    create_aad_group_params = {        
       'groupName' : f"az-{request_type}-{params['requestId']}-group",
       'groupDesc' : f"Security group for {request_type}, request id : {params['requestId']}"        
    }
    create_aad_group_result = yield context.call_activity('fn-drbl-create-aad-security-group-activity', create_aad_group_params)

    # logging.warn(create_aad_group_result)
    add_aad_owner_params = {
        'groupId' : create_aad_group_result['id'],
        'ownerId' : owner['id']
    }    
    add_aad_owner_result = yield context.call_activity('fn-drbl-add-aad-group-owner-activity', add_aad_owner_params)
    
    add_aad_members_params = {
        'groupId' : create_aad_group_result['id'],
        'memberIdList' : getAadUserObjectIds(get_aad_users_result)
    }
    add_aad_members_result = yield context.call_activity('fn-drbl-add-aad-group-members-activity', add_aad_members_params)

    create_rg_params = {
        'subscriptionId' : subscription_id,
        'resourceGroupName': rg_name,
        'location': location,
        'requestType': request_type,
        'msxEngagementId' : msx_engmt_id
    }
    create_rg_result = yield context.call_activity('fn-drbl-create-rg-activity', create_rg_params)
        
    create_owner_role_asgmt_params = {        
        'subscriptionId' : subscription_id,
        'roleDefinitionId': f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/8e3af657-a8ff-443c-a75c-2fe8c4bcb635",
        'principalId': owner['id'],
        'scope': create_rg_result['id'],
    }
    create_role_asgmt_result = yield context.call_activity('fn-drbl-assign-rbac-role-activity', create_owner_role_asgmt_params)
    
    time.sleep(30)
    create_group_role_asgmt_params = {        
        'subscriptionId' : subscription_id,
        'roleDefinitionId': f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c",
        'principalId': create_aad_group_result['id'],
        'scope': create_rg_result['id'],
    }
    create_role_asgmt_result = yield context.call_activity('fn-drbl-assign-rbac-role-activity', create_group_role_asgmt_params)
    
    req_params = { 
                'id': params['requestId'],
                'requestType': request_type,
                'msxEngagementId' : msx_engmt_id,
                'ownerName': params['ownerName'],
                'ownerEmail': params['ownerEmail'],
                'approvedconsumption': params['consumption'],
                'client': client,
                'teamEmails': params['teamEmails'],
                'subscriptionId': subscription_id,
                'resourceGroupName': rg_name,
                'location': location,
                'lastrequestinitiatedDateTime': params['requestedDateTime'],
                'lastrequestapprovedDateTime': params['approvedDateTime'],
                'actualconsumption': '',
                'description': params['description'],
                'createdDateTime': datetime.utcnow().strftime("%Y/%m/%d, %H:%M:%S")
            }
    db_result = yield context.call_activity('fn-drbl-create-cosmosdb-item-activity', req_params)
    
    return [ create_aad_group_result, add_aad_owner_result, add_aad_members_result, 
            create_rg_result, create_role_asgmt_result, db_result ]

main = df.Orchestrator.create(orchestrator_function)
