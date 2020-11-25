from botocore.exceptions import ClientError
import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:  
        # log event and extract its parameters
        logger.info("Starting list_tfe_orgs ...")
        logger.info(f"event = '{event}'")
        org_name = ''
        try:
            org_name = event["org_name"]
            logger.info(f"org_name = '{org_name}'")
        except:
            pass
        tfe_api_token = os.environ['TFE_API_TOKEN']
        logger.info(f"tfe_api_token: '{tfe_api_token[:10]}...'")
        
        headers = { 
            'authorization': 'Bearer ' + tfe_api_token,
            'content-type': 'application/vnd.api+json',
        }
        tfe_url_trunk = 'https://app.terraform.io/api/v2/'
        tfe_url_method = tfe_url_trunk + 'organizations/' + org_name
        response = requests.get(
            tfe_url_method,
            headers = headers,
            verify = True)
        data = response.json()['data']
        for item in data:
            logger.info(item['id'])

        logger.info("... finishing list_tfe_orgs.")

    except ClientError as e:
        logger.error("*** Error in list_tfe_orgs: {}".format(e))
        raise
