import logging
import json
import os
from datetime import datetime
import time 
import azure.durable_functions as df

# def getRequestId():    
#     return uuid.uuid4().hex[:6]   


# def getUserIds(teamEmails):
#     if (teamEmails):
#         emailList = teamEmails.split(';')
#         userIdList = []
#         for email in emailList:
#             x = email.split('@')            
#             userIdList.append(x[0])
#         return list(set(userIdList))
#     else:
#         return []

# def getAadUserObjectIds(aadUsersList):
#     if (aadUsersList):
#         userAadObjectIds = []
#         for user in aadUsersList:
#             userAadObjectIds.append(user['id'])
#         return userAadObjectIds
#     else:
#         return []     


def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info("Starting execution of orchastrator function")

    #Get parameters from input
    params = context.get_input()    
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']

    if ('consumption' in params):
      consumption = params['consumption']
    else:
      consumption = 1000

    if ('requestedDateTime' in params):
      requestedDateTime = params['requestedDateTime']
    else:
      requestedDateTime = datetime.utcnow().strftime("%Y/%m/%d, %H:%M:%S")

    if ('approvedDateTime' in params):
      approvedDateTime = params['approvedDateTime']
    else:
      approvedDateTime = datetime.utcnow().strftime("%Y/%m/%d, %H:%M:%S")
    
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
        request_type = 'lab-exercise'
        msx_engmt_id = 'NA'
        client = 'NA'

    if ('resourceGroupName' in params):
        rg_name = params['resourceGroupName']
    else: 
        rg_name = f"az-{request_type}-{params['ownerName']}-{params['requestId']}-rg"    
    
    if ('location' in params):
        location = params['location']
    else: 
        location = "eastus"

    create_sql_server = 'azlabssqlserver' + params['requestId']
    create_sql_mi = 'azlabssqlmi' + params['requestId']
    azuredmsservicename = 'azlabsdmsservice' + params['requestId']
    azuredmsvnetname = 'azlabsdmsvnet' + params['requestId']
    azuredmssubnetname = 'azlabsdmssubnet' + params['requestId']
    cosmosdbaccountname = 'cosmosaccount' + params['requestId']

    
    # get_aad_owner_result = yield context.call_activity('fn-drbl-list-aad-users-activity', { 'upnList': [ f"{params['ownerEmail']}"] })    
    # if (get_aad_owner_result):
    #     owner = get_aad_owner_result[0]
    # logging.warning(owner)

    # userIdList = getUserIds(params['teamEmails'])
    # # logging.warning(userIdList)
    # if (userIdList):
    #     get_aad_users_result = yield context.call_activity('fn-drbl-list-aad-users-activity', { 'upnList': userIdList } )
    #     # logging.warning(get_aad_users_result[0])
    # else: 
    #     get_aad_users_result = owner
    
    #create_aad_group_params = {        
       #'groupName' : f"az-{request_type}-{params['requestId']}-group",
       #'groupDesc' : f"Security group for {request_type}, request id : {params['requestId']}"        
    #}
    #create_aad_group_result = yield context.call_activity('fn-drbl-create-aad-security-group-activity', create_aad_group_params)

    # logging.warn(create_aad_group_result)
    #add_aad_owner_params = {
        #'groupId' : create_aad_group_result['id'],
        #'ownerId' : owner['id']
    #}    
    #add_aad_owner_result = yield context.call_activity('fn-drbl-add-aad-group-owner-activity', add_aad_owner_params)
    
    #add_aad_members_params = {
        #'groupId' : create_aad_group_result['id'],
        #'memberIdList' : getAadUserObjectIds(get_aad_users_result)
    #}
    #add_aad_members_result = yield context.call_activity('fn-drbl-add-aad-group-members-activity', add_aad_members_params)

    create_rg_params = {
        'subscriptionId' : subscription_id,
        'resourceGroupName': rg_name,
        'location': location,
        'requestType': request_type,
        'msxEngagementId' : msx_engmt_id
    }
    create_rg_result = yield context.call_activity('fn-drbl-create-rg-activity', create_rg_params)
        
    create_contributor_role_asgmt_params = {        
        'subscriptionId' : subscription_id,
        'roleDefinitionId': f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c",
        'principalId': '9778507b-4298-4a84-9c54-530c0543c3a8',
        'scope': create_rg_result['id'],
    }
    create_role_asgmt_result = yield context.call_activity('fn-drbl-assign-rbac-role-activity', create_contributor_role_asgmt_params)
    # time.sleep(30)

    if ('typeOfService' in params):
        typeofservices = params['typeOfService']
    else: 
        typeofservices = "sqldb"

    if(typeofservices == "sqlmi"):  
        deploy_template_params = {        
       'deploymentName' : 'deploy_sql_mi',       
       'subscriptionId' : subscription_id,       
       'resourceGroupName' : rg_name,       
       'templateLinkUri' : 'https://raw.githubusercontent.com/CSALabsAutomation/quickstart-templates/main/sqlmi/sql-mi-arm.json',
       'templateParams' : { 
                      'managedInstanceName': {
                          'value' : create_sql_mi
                                    },
                      'administratorLogin': {
                          'value': 'sqladmin'
                                            },
                      'administratorLoginPassword': {
                           'value': 'Sariyu@123'
                                                    }
                        }

    }
    elif(typeofservices == "azuredms"):  
        deploy_template_params = {        
       'deploymentName' : 'deploy_azure_dms',       
       'subscriptionId' : subscription_id,       
       'resourceGroupName' : rg_name,       
       'templateLinkUri' : 'https://raw.githubusercontent.com/CSALabsAutomation/quickstart-templates/main/azuredms/sql-dms.json',
       'templateParams' : { 
                      'serviceName': {
                          'value' : azuredmsservicename
                                    },
                      'vnetName': {
                          'value': azuredmsvnetname
                                  },
                      'subnetName': {
                           'value': azuredmssubnetname
                                    }
                        }

    }
    elif(typeofservices == "sqlvm"): 
        
        firstVNETName = 'vnet-01'
        firstVNETFESubnetName = 'subnet01'
        azurevmname = 'azlabssqlvm'


        pre_deploy_template_params = {        
       'deploymentName' : 'deploy_sql_vm',       
       'subscriptionId' : subscription_id,       
       'resourceGroupName' : rg_name,       
       'templateLinkUri' : 'https://raw.githubusercontent.com/CSALabsAutomation/quickstart-templates/main/sqlservices/sqlvm/prereq/prereq.azuredeploy.json',
       'templateParams' : {                      
                          }
        }
        pre_template_deployment = yield context.call_activity('fn-drbl-deploy-template-activity', pre_deploy_template_params)

        deploy_template_params = {        
       'deploymentName' : 'deploy_sql_vm_nextpart',       
       'subscriptionId' : subscription_id,       
       'resourceGroupName' : rg_name,       
       'templateLinkUri' : 'https://raw.githubusercontent.com/CSALabsAutomation/quickstart-templates/main/sqlservices/sqlvm/azuredeploy.json',
       'templateParams' : {  
                            'virtualMachineName': {
                            'value': azurevmname
                            },
                            'adminUsername': {
                            'value': 'sqladmin'
                            },
                            'adminPassword': {
                            'value': 'Sariyu@123'
                            },
                            'existingVirtualNetworkName': {
                            'value': firstVNETName
                            },
                            'existingSubnetName': {
                            'value': firstVNETFESubnetName
                            },
                            'existingVnetResourceGroup': {
                            'value': rg_name
                            }                   
                          }
    }
    elif(typeofservices == "cosmosdbsql"):  
        deploy_template_params = {        
       'deploymentName' : 'deploy_cosmos_db_sql',       
       'subscriptionId' : subscription_id,       
       'resourceGroupName' : rg_name,       
       'templateLinkUri' : 'https://raw.githubusercontent.com/CSALabsAutomation/quickstart-templates/main/cosmosdb-sql/azuredeploy.json',
       'templateParams' : { 
                            'accountName': {
                             'value' : cosmosdbaccountname
                                           },
                          'primaryRegion': {
                              'value': 'East US'
                                           },
                          'secondaryRegion': {
                              'value': 'West US'
                                             },
                          'databaseName': {
                              'value': 'myDatabase'
                                          },
                           'containerName': {
                              'value': 'myContainer'
                                            },
                           'throughput': {
                               'value': 400
                                         }
                                    
                        }
    }
    else:
        deploy_template_params = {        
         'deploymentName' : 'deploy_sql_server_db',       
         'subscriptionId' : subscription_id,       
         'resourceGroupName' : rg_name,       
         'templateLinkUri' : 'https://raw.githubusercontent.com/CSALabsAutomation/quickstart-templates/main/sqldb/sql-server.json',
         'templateParams' : { 
                      'serverName': {
                          'value' : create_sql_server
                                    },
                      'administratorLogin': {
                          'value': 'sqladmin'
                                            },
                      'administratorLoginPassword': {
                           'value': 'Sariyu@123'
                                                    }
                        }
    }
    
    template_deployment = yield context.call_activity('fn-drbl-deploy-template-activity', deploy_template_params)
    
    # return [ template_deployment]
    
    # for list_item in get_aad_users_result:
    #    create_contributor_role_asgmt_params_new = {        
    #     'subscriptionId' : subscription_id,
    #     'roleDefinitionId': f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c",
    #     'principalId': list_item['id'],
    #     'scope': create_rg_result['id'],
    #    }
    #    create_role_asgmt_result_new = yield context.call_activity('fn-drbl-assign-rbac-role-activity', create_contributor_role_asgmt_params_new)
    
    
    # time.sleep(30)
    # create_group_role_asgmt_params = {        
    #     'subscriptionId' : subscription_id,
    #     'roleDefinitionId': f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c",
    #     'principalId': create_aad_group_result['id'],
    #     'scope': create_rg_result['id'],
    # }
    # create_role_asgmt_result = yield context.call_activity('fn-drbl-assign-rbac-role-activity', create_group_role_asgmt_params)
    # time.sleep(30)
    req_params = { 
                'id': params['requestId'],
                'requestType': request_type,
                'msxEngagementId' : msx_engmt_id,
                'ownerName': params['ownerName'],
                'ownerEmail': params['ownerEmail'],
                'approvedconsumption': consumption,
                'client': client,
                'teamEmails': '',
                'subscriptionId': subscription_id,
                'resourceGroupName': rg_name,
                'location': location,
                'lastrequestinitiatedDateTime': requestedDateTime,
                'lastrequestapprovedDateTime': approvedDateTime,
                'actualconsumption': '',
                'description': '',
                'createdDateTime': datetime.utcnow().strftime("%Y/%m/%d, %H:%M:%S")
            }
    db_result = yield context.call_activity('fn-drbl-create-cosmosdb-item-activity', req_params)
    
    return [ #create_aad_group_result, add_aad_owner_result, add_aad_members_result, 
            create_rg_result, create_role_asgmt_result,template_deployment, db_result ]

main = df.Orchestrator.create(orchestrator_function)
