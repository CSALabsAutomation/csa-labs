import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentProperties, RoleAssignmentCreateParameters
import uuid

def main(params) -> dict:
    logging.info('Starting execution of the activity function')   

    try: 
        cred = DefaultAzureCredential() 
        auth_mgmt_client = AuthorizationManagementClient(cred, params['subscriptionId'])
        role_asgmt_props = RoleAssignmentProperties(role_definition_id=params['roleDefinitionId'], 
                                                    principal_id=params['principalId'])
        role_asgmt_create_parms=RoleAssignmentCreateParameters(properties=role_asgmt_props)
        role_assignment_name=str(uuid.uuid4())
        role_asgmt_client = auth_mgmt_client.role_assignments
        role_asgmt = role_asgmt_client.create(params['scope'], role_assignment_name, role_asgmt_create_parms)
        return role_asgmt.as_dict()
    except Exception as e:
        logging.exception(e)
        return str(e)
