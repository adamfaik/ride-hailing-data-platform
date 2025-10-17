from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys

# Add the 'include' folder to the Python path
# Replace with the absolute path to your include folder
sys.path.insert(0, '/Users/afaik.externe/Documents/GitHub/ride_hailing_platform/include')

from kafka_processing_dag2 import (
    consume_from_result_topic,
    transform_json,
    put_to_elasticsearch,
    put_to_gcp,
)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
}

with DAG(
    dag_id='dag_2_load_data',
    default_args=default_args,
    schedule=None, # Trigger manually for now
    catchup=False,
    tags=['kafka', 'gcp', 'elasticsearch'],
) as dag:

    consume_task = PythonOperator(
        task_id='consume_from_result_topic',
        python_callable=consume_from_result_topic
    )

    transform_task = PythonOperator(
        task_id='transform_json',
        python_callable=transform_json
    )

    # Define the two loading tasks
    load_to_elastic = PythonOperator(
        task_id='put_to_elasticsearch',
        python_callable=put_to_elasticsearch
    )

    load_to_gcp = PythonOperator(
        task_id='put_to_gcp',
        python_callable=put_to_gcp
    )

    # Define the task dependencies
    consume_task >> transform_task >> [load_to_elastic, load_to_gcp]