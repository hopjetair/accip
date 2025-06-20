# config.py
import os

api_key_secret_name = "api_secrets"
#api_key_secret_name_value = "api_key"

# Use environment variables with fallbacks for local development
nonprod = os.getenv("nonprod", "True").lower() == "true"
db_host = os.getenv("db_host", "localhost")  # "localhost")
db_name = os.getenv("db_name", "hopjetairline_db")
db_user = os.getenv("db_user", "postgres")
db_pass = os.getenv("db_pass", "Testing!@123")
db_port = os.getenv("db_port", "5433")  # Aurora default port is 5432

db_testname = os.getenv("db_testname", "test_hopjetairline_db")

# AWS configuration
aws_region = os.getenv("aws_region", "ap-southeast-2")