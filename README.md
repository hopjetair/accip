# Hopjet Airlines Customer Conversational Intelligence Platform

A Python-based project to manage an airline database using FastAPI and PostgreSQL, with data generation and testing capabilities.

## Overview

This project includes:

- A FastAPI API (`src/api/`) for managing airline operations (e.g., bookings, flights).
- A data generation module (`src/data/`) to populate the database with mock data.
- Unit tests (`tests/`) for validating functionality.
- A PostgreSQL database (`hopjetairline_db`) hosted locally or on AWS RDS.

## Prerequisites

- Python 3.8+
- PostgreSQL (local or AWS RDS)
- pip (for dependency management)

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd accip
   ```

### Installation

1. Clone this repository to your local machine.

2. Navigate to the project directory in your terminal.

3. Create a virtual environment:

   ```
   python -m venv application
   ```

### Activate the virtual environment:

#### On Windows

    .\application\Scripts\activate

#### On macOS/Linux

    source application/bin/activate

### Install the required dependencies

```
  pip install -r requirements.txt
```

### Running the Project

Once the environment is activated, run the main Python script:

    For Non-Ai APIs
        For Fastapi to run
            uvicorn src.api.main:app --reload --port 8003 --host 0.0.0.0
        For Unittest to run (broken for now)
            python -m unittest tests/test_api.py -v

### AWS

        How to connect github workflows and AWS with OCID
            https://www.youtube.com/watch?v=aOoRaVuh8Lc&list=PL5-Ls12B-Wv4IS1bH639RS7pv57ptFPbr&index=4&ab_channel=CodeMadeSimple

### Github

        How to work with multiple GitHub accounts on a single Windows computer using SSH
            https://www.youtube.com/watch?v=Fyfp0oEWD6w&list=PL5-Ls12B-Wv4IS1bH639RS7pv57ptFPbr&index=6&ab_channel=fromDev2Dev

### Database setup

    For PostgresSql
         Database Creation
                AWS
                    Use the console to create the database (free tier) (https://www.youtube.com/watch?v=YxMibQv7w8o&list=PL5-Ls12B-Wv4IS1bH639RS7pv57ptFPbr&index=2&t=326s&ab_channel=ProgrammingKnowledge  https://www.youtube.com/watch?v=vw5EO5Jz8-8&ab_channel=BeABetterDev)
                    DB name : hopjetairline_db
                    DB user : hopjetair
                    DB password : SecurePass123!
                    Store this credentials in AWS Secrets Manager
                        Secret name : db_credentials
                        Secret value = {"db_user":"hopjetair","db_pass":"SecurePass123!"}

               Locally
                    Install postgres for windows (https://www.postgresql.org/download/windows/)
                    DB password : Testing!@123  (Remarks : or what ever you want or have if you already have postgresql on your machine)
                    use this password to replace  os.environ["db_adminpass"] = "Testing!@123" in new_generator.py.

                    > python db_infra\scripts\generator.py uselocaldb   #(this will create the database and create datal)

                    > python .\db_infra\scripts\verify_records.py  uselocaldb  #(this will give the count of records in each table)

                    > python .\db_infra\scripts\purge_records.py  uselocaldb  #(this will delete all the records in each table)

### Create a AWS Fargate Cluster

        https://www.youtube.com/watch?v=1n46Nudo6Yo&t=19s&ab_channel=DigitalCloudTraining

### Create a AWS ECR

        Lifecycle Policy

### Create an Aurora and RDS Postgressql

        https://www.youtube.com/watch?v=YxMibQv7w8o&list=PL5-Ls12B-Wv4IS1bH639RS7pv57ptFPbr&index=2&t=326s&ab_channel=ProgrammingKnowledge

        Create a database instance
                Free tier
                Take the user and password from the secret manager

        Once created, set inbound rule for data to be accessed

### Github action

        Here i have a setup for my aws, once i create the aws thing hopjetair aws

        At present all are manual trigger, in prod we will trigger on build

            .github\workflows\aurora-airline-setup.yml
                This file create a database if doest not exist, run the schema and creates dummy data to AWS RDS

            .github\workflows\ecr.yml
                This  file create the docker image, does the test and deploy the image to ECR

            .github\workflows\ecs.yml
                This file creates and deploys the fargate task on ECS -> Service, it gets trigger only if ect.yml is successfull.

### VPC

        https://docs.aws.amazon.com/vpc/latest/userguide/vpc-example-dev-test.html#create-vpc-one-public-subnet

        https://www.youtube.com/watch?v=ApGz8tpNLgo&ab_channel=BeABetterDev

### Ecs fargate static elastic ip address

        https://repost.aws/knowledge-center/ecs-fargate-static-elastic-ip-address

        https://www.youtube.com/watch?v=o7s-eigrMAI&ab_channel=BeABetterDev
