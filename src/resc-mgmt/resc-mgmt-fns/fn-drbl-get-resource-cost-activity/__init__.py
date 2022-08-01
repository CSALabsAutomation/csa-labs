import logging
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient
from datetime import datetime, timezone
from azure.mgmt.costmanagement.models import ( QueryDefinition, ExportType, TimeframeType, QueryTimePeriod, 
        GranularityType, QueryDataset, QueryAggregation, QueryGrouping)

def main(params) -> dict:
    logging.info('Starting execution of the activity function')       
    try: 
        from_datetime =  datetime.strptime(params['fromDatetime'], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        to_datetime = datetime.strptime(params['toDatetime'], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        
        cred = DefaultAzureCredential()         
        cost_mgmt_client = CostManagementClient(cred, 'https://management.azure.com')
        query_dataset = QueryDataset(
                granularity=GranularityType("Daily"),                
                # configuration=QueryDatasetConfiguration(), 
                aggregation={"totalCost" : QueryAggregation(name="PreTaxCost", function ="Sum")}, 
                grouping=[QueryGrouping(type="Dimension", name="ResourceGroup")], 
                # filter = QueryFilter()
            )
        
        query_def = QueryDefinition(
            type=ExportType("Usage"),
            timeframe=TimeframeType("Custom"),            
            time_period=QueryTimePeriod(from_property=from_datetime, to=to_datetime),
            dataset=query_dataset
        )
        query_result = cost_mgmt_client.query.usage(scope=params['scope'], parameters=query_def)
        return query_result.as_dict()        
    except Exception as e:
        logging.exception(e)
        return str(e)


