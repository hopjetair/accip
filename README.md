# Airline Customer Conversational Intelligence Platform

A Python-based project to manage an airline database using FastAPI and PostgreSQL, with data generation and testing capabilities.

## Overview

This project includes:

- A FastAPI API (`src/api/`) for managing airline operations (e.g., bookings, flights).
- A data generation module (`src/data/`) to populate the database with mock data.
- Unit tests (`tests/`) for validating functionality.
- A PostgreSQL database (`airline_db`) hosted locally or on AWS RDS.

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

    For PostgresSql database
        Schema
            db_infra\scripts\create_airline_schema.sql

    For Mock data generation
        Data Generation
            python db_infra\scripts\generator.py
        For Unittest to run
            python -m unittest tests/test_data_generator.py -v


        Large dataset (1700) records in total loaded into PostgreSQL successfully.

    For Non-Ai APIs
        For Fastapi to run
            uvicorn src.api.main:app --reload --port 8003 --host 0.0.0.0
        For Unittest to run
            python -m unittest tests/test_api.py -v
