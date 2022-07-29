import logging
import json
from collections import namedtuple
from urllib import response
import azure.functions as func
import azure.durable_functions as df

ResQueryParams = namedtuple('Params', ['subscriptionId', 'query'])

SqlDpParams = namedtuple('Params', ['subscriptionId', 'resourceGroupName', 
                                'workspaceName', 'sqlPoolName'])

def get_sqldp_params_list(subscription_id, sqldp_list):
    sqldp_params_list = []
    for sqldp in sqldp_list: 
            sqldp_params_list += [ SqlDpParams(subscriptionId= subscription_id, 
                     resourceGroupName = sqldp['resourceGroup'],
                     workspaceName= sqldp['id'].split('/')[8],
                     sqlPoolName= sqldp['name']) ]
    return sqldp_params_list
    
def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info("Starting execution of orchastrator function")

    #Get subscription id from input
    params = context.get_input()
    subscription_id = params['subscriptionId']
    
    if (subscription_id):
        #Get the list of dedicated pools in the subscription
        query= 'project id, name, type, status=properties.status, resourceGroup | where type =~ "microsoft.synapse/workspaces/sqlpools"'
        res_query_params = ResQueryParams(subscriptionId=subscription_id, query=query)
        query_result = yield context.call_activity('fn-drbl-query-resource-graph-activity', res_query_params)
        sqldp_list = query_result['data']
        #Pause the dedicated pools
        sqldp_params_list = get_sqldp_params_list(subscription_id, sqldp_list)
        sqldp_result_tasks = [ context.call_activity('fn-drbl-pause-sql-dp-activity', sqldp_params) for sqldp_params in sqldp_params_list]
        
        #Combine and return the results
        sqldp_result = yield context.task_all(sqldp_result_tasks)
        return sqldp_result
    else:
        return "Please provide subscription id"

main = df.Orchestrator.create(orchestrator_function)