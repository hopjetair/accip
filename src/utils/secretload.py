# secretload.py
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
import json
import os
from config import *

def get_secret(secret_name):
    region_name = os.getenv(const_fieldname_aws_region, aws_region)
    try:
        #raise NoCredentialsError()            
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=region_name)
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        secret_dict = json.loads(secret)
        for key, value in secret_dict.items():
            os.environ[key] = value
    except NoCredentialsError as e:
        print(f"Error retrieving secret {secret_name}: {e}")
        if os.getenv(const_fieldname_nonprod, "True").lower() == "true":
            # Fallback for nonprod environment (local development)
            if secret_name == const_db_credentials_name:
                os.environ[const_fieldname_db_user] = os.getenv(const_fieldname_db_user,db_user)
                os.environ[const_fieldname_db_pass] = os.getenv(const_fieldname_db_pass, db_pass)
            elif secret_name == const_api_key_secret_name:
                os.environ["api_key"] = os.getenv("api_key","api_key")
                os.environ["api_secret"] = os.getenv("api_secret","")

if __name__ == "__main__":
    get_secret(const_db_credentials_name)
    get_secret(const_api_key_secret_name)