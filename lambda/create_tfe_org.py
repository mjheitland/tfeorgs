from botocore.exceptions import ClientError
import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:  
        # log event and extract its parameters
        logger.info("Starting create_tfe_org ...")
        logger.info("event = {}".format(event))
        app_name = event["app_name"]
        logger.info(f"app_name = {app_name}")
        logger.info("... finishing create_tfe_org.")
    except ClientError as e:
        logger.error("*** Error in create_tfe_org: {}".format(e))
        raise
