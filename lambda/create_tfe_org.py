from botocore.exceptions import ClientError
import json
import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:  
        # log event and extract its parameters
        logger.info("Starting create_tfe_org ...")
        logger.info(f"event = '{event}'")
        org_name = event["org_name"]
        logger.info(f"org_name = '{org_name}'")
        user_email = event["user_email"]
        logger.info(f"user_email = '{user_email}'")
        environment = event["environment"]
        logger.info(f"environment = '{environment}'")
        tfe_api_token = os.environ['TFE_API_TOKEN']
        logger.info(f"tfe_api_token: '{tfe_api_token[:10]}...'")
        
        headers = { 
            'authorization': 'Bearer ' + tfe_api_token,
            'content-type': 'application/vnd.api+json',
        }
        tfe_url_trunk = 'https://app.terraform.io/api/v2/'
        tfe_url_method = tfe_url_trunk + 'organizations'
        payload = {
            "data": {
                "type": "organizations",
                "attributes": {
                    "name": org_name,
                    "email": user_email
                }
            }
        }
        response = requests.post(
            tfe_url_method,
            headers = headers,
            data = json.dumps(payload),
            verify = True)
        data = response.json()['data']
        for item in data:
            logger.info(item['id'])

        logger.info("... finishing create_tfe_org.")

    except ClientError as e:
        logger.error("*** Error in create_tfe_org: {}".format(e))
        raise
