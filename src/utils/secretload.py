# secretload.py
import boto3
from botocore.exceptions import ClientError
import json
import os
import config

def get_secret(secret_name):
    region_name = os.getenv("aws_region", config.aws_region)
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        secret_dict = json.loads(secret)
        for key, value in secret_dict.items():
            os.environ[key] = value
    except ClientError as e:
        print(f"Error retrieving secret {secret_name}: {e}")
        if os.getenv("nonprod",config.nonprod).lower() == "true":
            # Fallback for nonprod environment (local development)
            if secret_name == "db_credentials":
                os.environ["db_user"] = os.getenv("db_user",config.db_user)
                os.environ["db_pass"] = os.getenv("db_pass", config.db_pass)
            elif secret_name == "api_secrets":
                os.environ["api_key"] = os.getenv("api_key","api_key")
                os.environ["api_secret"] = os.getenv("api_secret")

if __name__ == "__main__":
    get_secret("db_credentials")
    get_secret("api_secrets")