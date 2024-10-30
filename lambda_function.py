from boto3 import client
from os import environ
import logging
from .src.lambda_s3_store_to_rds.handle_image_store import ImageStorer

_LAMBDA_RDS_CLIENT = client('rds')

_LAMBDA_RDS_CONFIG = { "table_name" : environ.get("RDS_TABLE_NAME","NONE"),
                       "proxy_host_name" : environ.get("PROXY_HOST_NAME","NONE"),
                       "port" : int(environ.get("PORT","NONE")),
                       "db_name" : environ.get("DB_NAME","NONE"),
                       "db_user_name" : environ.get("DB_USER_NAME", "NONE"),
                       "aws_region" :environ.get("AWS_REGION", "NONE")}
_LAMBDA_S3_CLIENT =  client('s3')

def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    storer = ImageStorer( _LAMBDA_RDS_CONFIG, _LAMBDA_RDS_CLIENT, _LAMBDA_S3_CLIENT, logger)
    storer.handle(event)