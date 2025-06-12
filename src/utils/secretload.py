# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import boto3
from botocore.exceptions import ClientError
import json
import os
#from config import config
from config import *


def get_secret(secret_name):

    #"prod_api_key"
    secret_name = secret_name
    region_name = "ap-southeast-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    if not nonprod :
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise e
            
            

        secret = get_secret_value_response['SecretString']
        secret=json.loads(secret)
        for key, value in secret.items():os.environ[key] = value
    else:
        if(secret_name == 'db_pass'):
            os.environ[secret_name] = {db_pass}
        else:
            os.environ[secret_name] = secret_name   #config. "Capst0neo3@2024"

    # Your code goes here.
get_secret("prod_api_key")