# secretload.py
import boto3
from botocore.exceptions import ClientError
import json
import os

def get_secret(secret_name):
    region_name = os.getenv("AWS_REGION", "ap-southeast-2")
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
        if os.getenv("NONPROD", "True").lower() == "true":
            # Fallback for nonprod environment (local development)
            if secret_name == "db_credentials":
                os.environ["db_user"] = os.getenv("DB_USER", "postgres")
                os.environ["db_pass"] = os.getenv("DB_PASS", "Testing!@123")
            elif secret_name == "api_secrets":
                os.environ["api_key"] = os.getenv("API_KEY", "my-secret-key")
                os.environ["api_secret"] = os.getenv("API_SECRET", "Capst0neo3@2024")

if __name__ == "__main__":
    get_secret("db_credentials")
    get_secret("api_secrets")