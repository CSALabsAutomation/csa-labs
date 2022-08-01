import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import ( Deployment, DeploymentProperties, TemplateLink)


def main(params) -> dict:
    logging.info('Starting execution of the activity function')   
    try: 
        cred = DefaultAzureCredential() 
        resource_client = ResourceManagementClient(cred, params['subscriptionId'])                
        if not 'mode' in params: 
            mode='Incremental'
        else:
            mode = params['mode'] 
                        
        deployment_properties = DeploymentProperties(
                template_link = TemplateLink(uri=params['templateLinkUri']), 
                parameters = params['templateParams'], 
                mode='incremental'
        )

        result = resource_client.deployments.begin_create_or_update(
                resource_group_name = params['resourceGroupName'], 
                deployment_name = params['deploymentName'], 
                parameters= Deployment(properties=deployment_properties)
        )
        return result.result().properties.as_dict()
    except Exception as e:
        logging.exception(e)
        return str(e)