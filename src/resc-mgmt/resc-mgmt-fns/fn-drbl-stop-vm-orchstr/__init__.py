import logging
import json
from collections import namedtuple
import azure.durable_functions as df

ResQueryParams = namedtuple('Params', ['subscriptionId', 'query'])

vmParams = namedtuple('Params', ['subscriptionId', 'resourceGroupName', 'vmName'])

def get_vm_params_list(subscription_id, vm_list):
    vm_params_list = []
    for vm in vm_list: 
            vm_params_list += [ vmParams(subscriptionId= subscription_id, 
                     resourceGroupName = vm['resourceGroup'],
                     vmName= vm['name']) ]
    return vm_params_list
    
def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info("Starting execution of orchastrator function")

    #Get subscription id from input
    params = context.get_input()
    subscription_id = params['subscriptionId']
    
    if (subscription_id):
        #Get the list of VMs in the subscription
        query= 'project id, name, type, status=properties.status, resourceGroup | where type =~ "microsoft.compute/virtualmachines"'
        res_query_params = ResQueryParams(subscriptionId=subscription_id, query=query)
        query_result = yield context.call_activity('fn-drbl-query-resource-graph-activity', res_query_params)
        vm_list = query_result['data']
        #Stop the vms
        vm_params_list = get_vm_params_list(subscription_id, vm_list)
        vm_result_tasks = [ context.call_activity('fn-drbl-stop-vm-activity', vm_params) for vm_params in vm_params_list]
        
        #Combine and return the results
        vm_result = yield context.task_all(vm_result_tasks)
        return vm_result
    else:
        return "Please provide subscription id"

main = df.Orchestrator.create(orchestrator_function)