# config.py
import os

#constant
const_localhost  = "localhost"  # "localhost"

const_db_user = "hopjetair"  # user for the database
const_db_pass = "SecurePass123!"  # password for the databaser

const_db_adminuser = "postgres"  # user for the admin account
const_db_adminpass = "Testing!@123"  # password for the admin account

const_cloudhost = "postgressql-hopjetairline-1.cniwous8qb34.ap-southeast-2.rds.amazonaws.com"

const_api_key_secret_name = "api_secrets"
const_db_credentials_name = "db_credentials"
#constant field name
const_fieldname_db_host = "db_host"

const_fieldname_db_name = "db_name"

const_fieldname_db_user = "db_user"
const_fieldname_db_pass = "db_pass"

const_fieldname_db_port = "db_port"

const_fieldname_nonprod = "nonprod"

const_fieldname_aws_region = "aws_region"




# Use environment variables with fallbacks for local development
nonprod = os.getenv(const_fieldname_nonprod, "True").lower() == "true"
if nonprod:
    db_host = os.getenv(const_fieldname_db_host, "localhost")  # "localhost")
else :
    db_host = os.getenv(const_fieldname_db_host, const_cloudhost)  # "localhost")
    
db_name = os.getenv(const_fieldname_db_name, "hopjetairline_db")
db_user = os.getenv(const_fieldname_db_user, const_db_user)
db_pass = os.getenv(const_fieldname_db_pass, const_db_pass)
db_port = os.getenv(const_fieldname_db_port, "5432")  # Aurora default port is 5432

# for postgres database only
db_adminuser = os.getenv(const_fieldname_db_user, "postgres")
db_adminpass = os.getenv(const_fieldname_db_pass, "Testing!@123")

db_testname = os.getenv("db_testname", "test_hopjetairline_db")

# AWS configuration
aws_region = os.getenv(const_fieldname_aws_region, "ap-southeast-2")


