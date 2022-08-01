import logging
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    logging.info("Starting execution of orchastrator function")

    #Get parameters from input
    params = context.get_input()        
    
    deploy_template_params = {        
       'deploymentName' : params['deploymentName'],       
       'subscriptionId' : params['subscriptionId'],       
       'resourceGroupName' : params['resourceGroupName'],       
       'templateLinkUri' : params['templateLinkUri'],
       'templateParams' : params['templateParams']
    }
    
    template_deployment = yield context.call_activity('fn-drbl-deploy-template-activity', deploy_template_params)
    
    return [ template_deployment]

main = df.Orchestrator.create(orchestrator_function)