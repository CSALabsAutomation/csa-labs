import logging
import json
import os
from datetime import datetime
import time 
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info("Starting execution of orchastrator function")

    #Get parameters from input
    params = context.get_input()    
    # subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
        
    
    get_resource_cost_params = {        
       'fromDatetime' : params['fromDatetime'],
       'toDatetime' : params['toDatetime'],
       'scope': params['scope']
    }
    
    get_resource_cost = yield context.call_activity('fn-drbl-get-resource-cost-activity', get_resource_cost_params)
    
    return [ get_resource_cost]

main = df.Orchestrator.create(orchestrator_function)