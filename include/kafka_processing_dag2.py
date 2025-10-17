import json
import os
from datetime import datetime
import requests
from confluent_kafka import Consumer
from google.cloud import storage

# --- Configuration ---
KAFKA_BROKER_URL = 'localhost:9092'
SOURCE_TOPIC = 'topic_result'
ELASTICSEARCH_URL = "http://localhost:9200/ride_hailing_trips/_doc"
GCP_BUCKET_NAME = "ride-hailing-platform-bucket-2025"
GCP_KEYFILE_PATH = "gcp-credentials.json"

def consume_from_result_topic():
    """Consumes a single message from the result Kafka topic."""
    conf = {
        'bootstrap.servers': KAFKA_BROKER_URL,
        'group.id': 'airflow-dag2-consumer',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe([SOURCE_TOPIC])

    msg = consumer.poll(timeout=5.0)
    consumer.close()

    if msg is None:
        print("No new messages found in topic_result.")
        return None
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        return None

    message_value = json.loads(msg.value().decode('utf-8'))
    print(f"Consumed message from result topic: {message_value}")
    return message_value

def transform_json(**kwargs):
    """Flattens the JSON and adds a timestamp."""
    ti = kwargs['ti']
    message_data = ti.xcom_pull(task_ids='consume_from_result_topic')

    if not message_data:
        print("No data received. Skipping transform.")
        return None

    # Extract the core data object
    trip_info = message_data['data'][0]
    client_props = trip_info['properties-client']
    driver_props = trip_info['properties-driver']

    # Flatten the structure
    flattened_data = {
        "nomclient": client_props.get("nomclient"),
        "telephoneClient": client_props.get("telephoneClient"),
        "locationClient": client_props.get("location"),
        "distance": trip_info.get("distance"),
        "confort": trip_info.get("confort"),
        "prix_travel": trip_info.get("prix_travel"),
        "nomDriver": driver_props.get("nomDriver"),
        "locationDriver": driver_props.get("location"),
        "telephoneDriver": driver_props.get("telephoneDriver"),
        "agent_timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    print(f"Transformed data: {flattened_data}")
    return flattened_data

def put_to_elasticsearch(**kwargs):
    """Sends the transformed JSON to Elasticsearch."""
    ti = kwargs['ti']
    data_to_push = ti.xcom_pull(task_ids='transform_json')

    if not data_to_push:
        print("No data received. Skipping Elasticsearch load.")
        return

    try:
        response = requests.post(ELASTICSEARCH_URL, json=data_to_push)
        response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
        print(f"Successfully pushed to Elasticsearch. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error pushing to Elasticsearch: {e}")
        raise

def put_to_gcp(**kwargs):
    """Sends the transformed JSON to Google Cloud Storage."""
    ti = kwargs['ti']
    data_to_push = ti.xcom_pull(task_ids='transform_json')

    if not data_to_push:
        print("No data received. Skipping GCS load.")
        return

    try:
        # Set credentials using the service account key
        storage_client = storage.Client.from_service_account_json(GCP_KEYFILE_PATH)

        # Get the bucket
        bucket = storage_client.bucket(GCP_BUCKET_NAME)

        # Define file name with a timestamp to ensure uniqueness
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
        destination_blob_name = f"data/trip_{timestamp}.json"

        # Create a blob and upload the data
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(json.dumps(data_to_push), content_type='application/json')

        print(f"Successfully uploaded to GCS bucket '{GCP_BUCKET_NAME}' as '{destination_blob_name}'.")
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        raise