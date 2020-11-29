#--- full_setup: create tfe org if it does not exist, add a workspace, connect it to GitHub, add TFE vars

from botocore.exceptions import ClientError
import json
import logging
import os
import requests

HTTP_OK = 200
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:  
        # log event and extract its parameters
        logger.info("Starting full_setup ...")
        logger.info(f"event = '{event}'")
        org_name = event["org_name"]
        logger.info(f"org_name = '{org_name}'")
        user_email = event["user_email"]
        logger.info(f"user_email = '{user_email}'")
        workspace_name = event["workspace_name"]
        logger.info(f"workspace_name = '{workspace_name}'")
        tfe_api_token = os.environ['TFE_API_TOKEN']
        logger.info(f"tfe_api_token: '{tfe_api_token[:10]}...'")
        
        headers = { 
            'authorization': 'Bearer ' + tfe_api_token,
            'content-type': 'application/vnd.api+json',
        }
        tfe_url_trunk = 'https://app.terraform.io/api/v2/'

        # check if a TFE org with org_name already exists
        tfe_url_method = tfe_url_trunk + 'organizations/' + org_name
        response = requests.get(
            tfe_url_method,
            headers = headers,
            verify = True)
        logger.info(response.json())
        if response.status_code == HTTP_OK:
            logger.info(f"TFE org '{org_name}' does exist")
        else:
            logger.info(f"TFE org '{org_name}' does not exist")
            logger.info(f"Creating TFE org '{org_name}' ...")
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
            logger.info(response.json())
            if response.status_code == HTTP_OK:
                logger.info(f"... TFE org '{org_name}' created.")
            else:
                logger.error(f"*** Error in full_setup: Couldn't create org '{org_name}': {response.json()}")

        logger.info("... finishing full_setup.")

    except ClientError as e:
        logger.error("*** Error in full_setup: {}".format(e))
        raise
