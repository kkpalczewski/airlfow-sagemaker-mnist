# Description
Basic Airflow with Sagemaker pipeline heavily inspired by `Data Pipelines with Apache Airflow` book.

# Usage
1. Fill template `.env.template` and then rename it to `.env` so that docker-compose would source it
2. Run docker-compose up
3. To expose Sagemaker Endpoint run Chalice from `app.py`

# Tests
Run `pytest tests`