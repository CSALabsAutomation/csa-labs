import logging
from collections import namedtuple
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

Params = namedtuple('Params', ['subscriptionId', 'resourceGroupName', 'vmName'])

def main(params: Params) -> str:
    logging.info('Starting execution of the activity function')   
    subscription_id, resource_group_name, vm_name = params    
    if (subscription_id and resource_group_name and vm_name):
        try: 
            cred = DefaultAzureCredential()
            mgmt_client = ComputeManagementClient(cred, subscription_id)
            vm_ops_client = mgmt_client.virtual_machines
            result = vm_ops_client.begin_deallocate(resource_group_name, vm_name)
            return { "vm_name": vm_name, "vm_stop_status": result.status() }
        except Exception as e:
            logging.exception(e)
            return str(e)
    else:
        return 'One or more required parameters are missing'
