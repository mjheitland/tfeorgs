from botocore.exceptions import ClientError
import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:  
        # log event and extract its parameters
        logger.info("Starting create_tfe_org ...")
        logger.info("event = {}".format(event))
        app_name = event["app_name"]
        logger.info(f"app_name = {app_name}")
        user_email = event["user_email"]
        logger.info(f"user_email = {user_email}")
        environment = event["environment"]
        logger.info(f"environment = {environment}")
        tfe_api_token = os.environ['TFE_API_TOKEN']
        logger.info(f"tfe_api_token: {tfe_api_token.sub[:10]}")
        logger.info("... finishing create_tfe_org.")
    except ClientError as e:
        logger.error("*** Error in create_tfe_org: {}".format(e))
        raise
