'''create tfe org with a workspace connected to GitHub repo and add TFE workspace vars'''
#pylint: disable=logging-fstring-interpolation
#pylint: disable=line-too-long

import json
import logging
import os
import requests
from botocore.exceptions import ClientError
#from collections import namedtuple

HTTP_OK = 200
HTTP_CREATED = 201
HTTP_NOT_FOUND = 404
TF_VERSION = "0.13.5"
TFE_URL_TRUNK = 'https://app.terraform.io/api/v2'
VCS_HTTP_URL = "https://github.com" # https://1.2.3.4
VCS_API_URL = "https://api.github.com" # https://1.2.3.4/api/v3
VERIFY_SSL = True

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#ExternalParameters = namedtuple('ExternalParameters',
#    ['org_name', 'user_email', 'workspace_name', 'repo_name', 'tfe_api_token', 'ghe_api_token'])

class ExternalParameters():
    '''Helper class for passing external parameters to methods to avoid too-many-parameters-warning'''
    #pylint: disable=too-few-public-methods
    #pylint: disable=too-many-arguments
    def __init__(
            self, org_name, user_email, workspace_name, repo_name,
            tfe_api_token, ghe_api_token) -> None:
        self.org_name       = org_name
        self.user_email     = user_email
        self.workspace_name = workspace_name
        self.repo_name      = repo_name
        self.tfe_api_token  = tfe_api_token
        self.ghe_api_token  = ghe_api_token
        self.headers        = {
            'authorization': 'Bearer ' + tfe_api_token,
            'content-type': 'application/vnd.api+json',
        }


class TfeVariable():
    '''Helper class for passing external parameters to methods to avoid too-many-parameters-warning'''
    #pylint: disable=too-few-public-methods
    #pylint: disable=too-many-arguments
    def __init__(self, key, value, description, hcl, sensitive, category) -> None:
        self.key            = key
        self.value          = value
        self.description    = description
        self.hcl                = hcl       # HCL type, e.g. list
        self.sensitive          = sensitive # sensitive values get encrypted
        self.category           = category  # either "terraform" or 'env'


def lambda_handler(event, context):
    '''main entry point'''
    #pylint: disable=unused-argument
    try:
        # log event and extract its parameters
        logger.info("Starting full_setup ...")
        logger.info(f"event = '{event}'")
        tfe_api_token = os.environ['TFE_API_TOKEN']
        logger.info(f"tfe_api_token: '{tfe_api_token[:10]}...'")
        ghe_api_token = os.environ['GHE_API_TOKEN'] # i.e. GHE Personal Access Token
        logger.info(f"ghe_api_token: '{ghe_api_token[:10]}...'")
        params = ExternalParameters(
            event["org_name"],
            event["user_email"],
            event["workspace_name"],
            event["repo_name"],
            tfe_api_token,
            ghe_api_token)

        create_org(params)

        tfe_vcs_token_id = get_tfe_vcs_token_id (params)

        workspace_id = create_workspace(params, tfe_vcs_token_id)

        create_workspace_variable(
            params,
            workspace_id,
            TfeVariable(
                'TF_VAR_TFE_API_TOKEN',
                params.tfe_api_token,
                'Terraform API token',
                False,
                True,
                'env'
            )
        )

        create_workspace_variable(
            params,
            workspace_id,
            TfeVariable(
                'TF_VAR_GHE_API_TOKEN',
                params.ghe_api_token,
                'GHE API token',
                False,
                True,
                'env'
            )
        )

        create_workspace_variable(
            params,
            workspace_id,
            TfeVariable(
                'AWS_DEFAULT_REGION',
                os.environ['AWS_REGION'],
                'AWS default region',
                False,
                False,
                'env'
            )
        )

        create_workspace_variable(
            params,
            workspace_id,
            TfeVariable(
                'AWS_ACCESS_KEY_ID',
                os.environ['COPY_AWS_ACCESS_KEY_ID'],
                'AWS access key',
                False,
                False,
                'env'
            )
        )

        create_workspace_variable(
            params,
            workspace_id,
            TfeVariable(
                'AWS_SECRET_ACCESS_KEY',
                os.environ['COPY_AWS_SECRET_ACCESS_KEY'],
                'AWS secret key',
                False,
                True,
                'env'
            )
        )

        create_workspace_variable(
            params,
            workspace_id,
            TfeVariable(
                'TF_VAR_COPY_AWS_ACCESS_KEY_ID',
                os.environ['COPY_AWS_ACCESS_KEY_ID'],
                'AWS secret key',
                False,
                False,
                'env'
            )
        )

        create_workspace_variable(
            params,
            workspace_id,
            TfeVariable(
                'TF_VAR_COPY_AWS_SECRET_ACCESS_KEY',
                os.environ['COPY_AWS_SECRET_ACCESS_KEY'],
                'AWS secret key',
                False,
                True,
                'env'
            )
        )

        logger.info("... finishing full_setup.")

    except ClientError as ex:
        logger.error(f"*** Error in full_setup: {ex}")
        raise

    except Exception as ex:
        logger.error(f"*** Error in full_setup: {ex}")
        raise


def create_org(params):
    '''create TFE org if it does not exist'''
    response = requests.get(
        f"{TFE_URL_TRUNK}/organizations/{params.org_name}",
        headers = params.headers,
        verify = VERIFY_SSL)
    logger.info(f"status_code: {response.status_code}")
    logger.info(response.json())
    if response.status_code not in [HTTP_OK, HTTP_NOT_FOUND]:
        raise Exception(f"Get TFE org call failed for org '{params.org_name}': {response.json()}")
    if response.status_code == HTTP_OK:
        logger.info(f"TFE org '{params.org_name}' already exists.")
    elif response.status_code == HTTP_NOT_FOUND:
        logger.info(f"TFE org '{params.org_name}' does not exist")
        logger.info(f"Creating TFE org '{params.org_name}' ...")
        payload = {
            "data": {
                "type": "organizations",
                "attributes": {
                    "name": params.org_name,
                    "email": params.user_email
                }
            }
        }
        response = requests.post(
            f"{TFE_URL_TRUNK}/organizations",
            headers = params.headers,
            data = json.dumps(payload),
            verify = VERIFY_SSL)
        logger.info(f"status_code: {response.status_code}")
        logger.info(response.json())
        if response.status_code != HTTP_CREATED:
            raise Exception(f"Couldn't create org '{params.org_name}': {response.json()}")
        logger.info(f"... TFE org '{params.org_name}' created.")


def get_tfe_vcs_token_id (params):
    '''create OAuth client if it does not exist'''
    tfe_url_method = f"{TFE_URL_TRUNK}/organizations/{params.org_name}/oauth-clients"
    response = requests.get(
        tfe_url_method,
        headers = params.headers,
        verify = VERIFY_SSL)
    logger.info(f"status_code: {response.status_code}")
    logger.info(response.json())
    if response.status_code not in [HTTP_OK]:
        raise Exception(
            f"Get TFE OAuth clients call failed for workspace '{params.org_name}': {response.json()}")
    data = response.json()['data']
    logger.info(data)
    if data:
        logger.info(f"TFE OAuth Client for '{params.org_name}' already exists.")
        tfe_vcs_token_id = data[0]["relationships"]["oauth-tokens"]["data"][0]["id"]
        logger.info(f"tfe_vcs_token_id: {tfe_vcs_token_id}")
    else:
        logger.info(f"TFE OAuth client for '{params.org_name}' does not exist")
        tfe_vcs_token_id = create_tfe_vcs_token_id(params)
        logger.info(f"... TFE OAuth client for '{params.org_name}' created.")

    return tfe_vcs_token_id


def create_tfe_vcs_token_id(params):
    """create a new Terraform OAutch client (i.e. connection between TFE and GHE)"""
    logger.info(f"Creating TFE OAuth client for '{params.org_name}' ...")
    tfe_url_method = f"{TFE_URL_TRUNK}/organizations/{params.org_name}/oauth-clients"
    payload = {
        "data": {
            "type": "oauth-clients",
            "attributes": {
                "service-provider": "github",
                "http-url": VCS_HTTP_URL,
                "api-url": VCS_API_URL,
                "oauth-token-string": params.ghe_api_token
            }
        }
    }
    response = requests.post(
        tfe_url_method,
        headers = params.headers,
        data = json.dumps(payload),
        verify = VERIFY_SSL)
    logger.info(f"status_code: {response.status_code}")
    logger.info(response.json())
    if response.status_code != HTTP_CREATED:
        raise Exception(
            f"Couldn't create OAuth client for '{params.org_name}': {response.json()}")
    data = response.json()['data']
    logger.info(data)
    tfe_vcs_token_id = data["relationships"]["oauth-tokens"]["data"][0]["id"]
    logger.info(f"tfe_vcs_token_id: {tfe_vcs_token_id}")
    return tfe_vcs_token_id


def create_workspace(params, tfe_vcs_token_id):
    '''create workspace if it does not exist'''
    tfe_url_method = f"{TFE_URL_TRUNK}/organizations/{params.org_name}/workspaces/{params.workspace_name}"
    response = requests.get(
        tfe_url_method,
        headers = params.headers,
        verify = VERIFY_SSL)
    logger.info(f"status_code: {response.status_code}")
    logger.info(response.json())
    workspace_id = ''
    if response.status_code not in [HTTP_OK, HTTP_NOT_FOUND]:
        raise Exception(
            f"Get TFE workspace call failed for '{params.org_name}/{params.workspace_name}': {response.json()}")
    if response.status_code == HTTP_OK:
        logger.info(f"TFE workspace '{params.org_name}/{params.workspace_name}' already exists.")
        workspace_id = response.json()["data"]["id"]
        logger.info(f"workspace_id: {workspace_id}")
    elif response.status_code == HTTP_NOT_FOUND:
        logger.info(f"TFE workspace '{params.org_name}/{params.workspace_name}' does not exist")
        logger.info(f"Creating TFE workspace '{params.org_name}/{params.workspace_name}' ...")
        tfe_url_method = f"{TFE_URL_TRUNK}/organizations/{params.org_name}/workspaces"
        payload = {
            "data": {
                "attributes": {
                    "name": params.workspace_name,
                    "terraform_version": TF_VERSION,
                    "working-directory": "",
                    "vcs-repo": {
                        "identifier": params.repo_name,
                        "oauth-token-id": tfe_vcs_token_id,
                        "ingress_submodules": True,
                        "branch": "",
                        "default-branch": True
                    }
                },
                "type": "workspaces"
            }
        }
        response = requests.post(
            tfe_url_method,
            headers = params.headers,
            data = json.dumps(payload),
            verify = VERIFY_SSL)
        logger.info(f"status_code: {response.status_code}")
        logger.info(response.json())
        if response.status_code != HTTP_CREATED:
            raise Exception(
                f"Couldn't create worksapce '{params.org_name}/{params.workspace_name}': {response.json()}")
        workspace_id = response.json()["data"]["id"]
        logger.info(f"workspace_id: {workspace_id}")
        logger.info(f"... TFE workspace '{params.org_name}/{params.workspace_name}' created.")
    return workspace_id


def create_workspace_variable(params, workspace_id, tfe_var):
    '''create workspace variable if it does not exist'''
    tfe_url_method = f"{TFE_URL_TRUNK}/workspaces/{workspace_id}/vars"
    response = requests.get(
        tfe_url_method,
        headers = params.headers,
        verify = VERIFY_SSL)
    logger.info(f"status_code: {response.status_code}")
    logger.info(response.json())
    if response.status_code not in [HTTP_OK]:
        raise Exception(
            f"Get var call failed for workspace '{params.org_name}/{params.workspace_name}': {response.json()}")
    data = response.json()["data"]
    key_found = False
    if len(data) > 0:
        for data_item in data:
            if data_item['attributes']['key'] == tfe_var.key:
                key_found = True
                break
    if key_found:
        logger.info(f"Variable '{tfe_var.key}' does already exist in '{params.org_name}/{params.workspace_name}'")
    else:
        logger.info(f"Variable '{tfe_var.key}' does not exist in '{params.org_name}/{params.workspace_name}'")
        logger.info(f"Creating TFE workspace variable '{tfe_var.key}' in '{params.org_name}/{params.workspace_name}' ...")
        tfe_url_method = f"{TFE_URL_TRUNK}/workspaces/{workspace_id}/vars"
        payload = {
            "data": {
                "type":"vars",
                "attributes": {
                "key":tfe_var.key,
                "value":tfe_var.value,
                "description":tfe_var.description,
                "category":tfe_var.category,
                "hcl":tfe_var.hcl,
                "sensitive":tfe_var.sensitive
                }
            }
        }
        response = requests.post(
            tfe_url_method,
            headers = params.headers,
            data = json.dumps(payload),
            verify = VERIFY_SSL)
        logger.info(f"status_code: {response.status_code}")
        logger.info(response.json())
        if response.status_code != HTTP_CREATED:
            raise Exception(
                f"Couldn't create '{tfe_var.key}' in '{params.org_name}/{params.workspace_name}': {response.json()}")
        logger.info(f"... variable '{tfe_var.key}' in '{params.org_name}/{params.workspace_name}' created.")
