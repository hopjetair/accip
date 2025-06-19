# config.py
import os

api_key_secret_name = "prod_api_key"
api_key_secret_name_value = "prod_api_value"

# Use environment variables with fallbacks for local development
nonprod = os.getenv("NONPROD", "True").lower() == "true"
db_host = os.getenv("DB_HOST", "localhost")
db_name = os.getenv("DB_NAME", "hopjetairline_db")
db_user = os.getenv("DB_USER", "postgres")
db_pass = os.getenv("DB_PASS", "Testing!@123")
db_port = os.getenv("DB_PORT", "5432")  # Aurora default port is 5432

db_testname = os.getenv("DB_TESTNAME", "test_hopjetairline_db")

# AWS configuration
aws_region = os.getenv("AWS_REGION", "ap-southeast-2")