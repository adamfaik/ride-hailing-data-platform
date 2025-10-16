from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
import sys

sys.path.insert(0, '/Users/afaik.externe/Documents/GitHub/ride_hailing_platform/include')

from kafka_processing import consume_from_kafka, compute_cost_travel, publish_to_kafka

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id='dag_1_trip_processing',
    default_args=default_args,
    schedule='@daily',
    catchup=False,
    tags=['kafka', 'ride_hailing'],
) as dag:

    consume_task = PythonOperator(
        task_id='consume_from_kafka',
        python_callable=consume_from_kafka
    )

    compute_task = PythonOperator(
        task_id='compute_cost_travel',
        python_callable=compute_cost_travel
    )

    publish_task = PythonOperator(
        task_id='publish_to_kafka',
        python_callable=publish_to_kafka
    )

    # Define the task dependencies
    consume_task >> compute_task >> publish_task