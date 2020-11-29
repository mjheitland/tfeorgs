#--- full_setup: create tfe org if it does not exist, add a workspace, connect it to GitHub, add TFE vars

from botocore.exceptions import ClientError
import json
import logging
import os
import requests

HTTP_OK         = 200
HTTP_CREATED    = 201
HTTP_NOT_FOUND  = 404
TF_VERSION      = "0.13.5"
TFE_URL_TRUNK   = 'https://app.terraform.io/api/v2'

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
        ghe_api_token = os.environ['GHE_API_TOKEN'] # i.e. GHE Personal Access Token
        logger.info(f"ghe_api_token: '{ghe_api_token[:10]}...'")
        
        headers = { 
            'authorization': 'Bearer ' + tfe_api_token,
            'content-type': 'application/vnd.api+json',
        }

        # create TFE org if it does not exist
        tfe_url_method = f"{TFE_URL_TRUNK}/organizations/{org_name}"
        response = requests.get(
            tfe_url_method,
            headers = headers,
            verify = True)
        logger.info(f"status_code: {response.status_code}")
        logger.info(response.json())
        if response.status_code not in [HTTP_OK, HTTP_NOT_FOUND]:
            raise Exception(f"Get TFE org call failed for org '{org_name}': {response.json()}")
        if response.status_code == HTTP_OK:
            logger.info(f"TFE org '{org_name}' already exists.")
        elif response.status_code == HTTP_NOT_FOUND:
            logger.info(f"TFE org '{org_name}' does not exist")
            logger.info(f"Creating TFE org '{org_name}' ...")
            tfe_url_method = f"{TFE_URL_TRUNK}/organizations"
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
            logger.info(f"status_code: {response.status_code}")
            logger.info(response.json())
            if response.status_code != HTTP_CREATED:
                raise Exception(f"Couldn't create org '{org_name}': {response.json()}")
            logger.info(f"... TFE org '{org_name}' created.")

        # create OAuth client if it does not exist
        tfe_url_method = f"{TFE_URL_TRUNK}/organizations/{org_name}/oauth-clients"
        response = requests.get(
            tfe_url_method,
            headers = headers,
            verify = True)
        logger.info(f"status_code: {response.status_code}")
        logger.info(response.json())
        if response.status_code not in [HTTP_OK]:
            raise Exception(f"Get TFE OAuth clients call failed for workspace '{org_name}/{workspace_name}': {response.json()}")
        data = response.json()['data']
        logger.info(data)
        if len(data) > 0:
            logger.info(f"TFE OAuth Client for '{org_name}/{workspace_name}' already exists.")
        else:
            logger.info(f"TFE OAuth client for '{org_name}/{workspace_name}' does not exist")
            logger.info(f"Creating TFE OAuth client for '{org_name}/{workspace_name}' ...")
            tfe_url_method = f"{TFE_URL_TRUNK}/organizations/{org_name}/oauth-clients"
            payload = {
                "data": {
                    "type": "oauth-clients",
                    "attributes": {
                        "service-provider": "github",
                        "http-url": "https://github.com",
                        "api-url": "https://api.github.com",
                        "oauth-token-string": ghe_api_token
                    }
                }
            }
            response = requests.post(
                tfe_url_method,
                headers = headers,
                data = json.dumps(payload),
                verify = True)
            logger.info(f"status_code: {response.status_code}")
            logger.info(response.json())
            if response.status_code != HTTP_CREATED:
                raise Exception(f"Couldn't create OAuth client for '{org_name}/{workspace_name}': {response.json()}")
            logger.info(f"... TFE OAuth client for '{org_name}/{workspace_name}' created.")
        return

        # create workspace if it does not exist
        tfe_url_method = f"{TFE_URL_TRUNK}/organizations/{org_name}/workspaces/{workspace_name}"
        response = requests.get(
            tfe_url_method,
            headers = headers,
            verify = True)
        logger.info(f"status_code: {response.status_code}")
        logger.info(response.json())
        if response.status_code not in [HTTP_OK, HTTP_NOT_FOUND]:
            raise Exception(f"Get TFE workspace call failed for workspace '{org_name}/{workspace_name}': {response.json()}")
        if response.status_code == HTTP_OK:
            logger.info(f"TFE workspace '{org_name}/{workspace_name}' already exists.")
        elif response.status_code == HTTP_NOT_FOUND:
            logger.info(f"TFE workspace '{org_name}/{workspace_name}' does not exist")
            logger.info(f"Creating TFE workspace '{org_name}/{workspace_name}' ...")
            tfe_url_method = f"{TFE_URL_TRUNK}/organizations/{org_name}/workspaces"
            payload = {
                "data": {
                    "attributes": {
                        "name": workspace_name,
                        "terraform_version": TF_VERSION,
                        "working-directory": "",
                        "vcs-repo": {
                            "identifier": "mjheitland/tfeorgs",
                            "oauth-token-id": "",
                            "ingress_submodules": True,
                            "branch": "",
                            "default-branch": true
                        }
                    },
                    "type": "workspaces"
                }
            }
            response = requests.post(
                tfe_url_method,
                headers = headers,
                data = json.dumps(payload),
                verify = True)
            logger.info(f"status_code: {response.status_code}")
            logger.info(response.json())
            if response.status_code != HTTP_CREATED:
                raise Exception(f"Couldn't create worksapce '{org_name}/{workspace_name}': {response.json()}")
            logger.info(f"... TFE org '{org_name}/{workspace_name}' created.")

        logger.info("... finishing full_setup.")

    except ClientError as e:
        logger.error("*** Error in full_setup: {}".format(e))
        raise

    except Exception as e:
        logger.error("*** Error in full_setup: {}".format(e))
        raise
