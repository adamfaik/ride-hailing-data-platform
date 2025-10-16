import json
from confluent_kafka import Consumer, Producer
from geopy.distance import geodesic

KAFKA_BROKER_URL = 'localhost:9092'
SOURCE_TOPIC = 'topic_source'
DESTINATION_TOPIC = 'topic_result'

def consume_from_kafka():
    """Consumes a single message from the source Kafka topic."""
    conf = {
        'bootstrap.servers': KAFKA_BROKER_URL,
        'group.id': 'airflow-dag1-consumer',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe([SOURCE_TOPIC])

    msg = consumer.poll(timeout=5.0) # Wait up to 5 seconds for a message
    consumer.close()

    if msg is None:
        print("No new messages found.")
        return None
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        return None

    # Return the message value as a dictionary
    message_value = json.loads(msg.value().decode('utf-8'))
    print(f"Consumed message: {message_value}")
    return message_value

def compute_cost_travel(**kwargs):
    """Calculates distance and price for a trip."""
    ti = kwargs['ti']
    message_data = ti.xcom_pull(task_ids='consume_from_kafka')

    if not message_data:
        print("No data received from previous task. Skipping.")
        return None

    trip_info = message_data['data'][0]
    client_props = trip_info['properties-client']
    driver_props = trip_info['properties-driver']

    client_coords = (client_props['latitude'], client_props['logitude'])
    driver_coords = (driver_props['latitude'], driver_props['logitude'])

    # Calculate distance
    distance_km = round(geodesic(client_coords, driver_coords).kilometers, 3)

    # Calculate price
    price_base = trip_info['prix_base_per_km']
    price_travel = round(distance_km * price_base, 2)

    # Build the enriched message
    enriched_data = {
        "data": [{
            "properties-client": {
                "nomclient": client_props['nomclient'],
                "telephoneClient": client_props['telephoneClient'],
                "location": f"{client_props['logitude']}, {client_props['latitude']}" # Format as string
            },
            "distance": distance_km,
            "properties-driver": {
                "nomDriver": driver_props['nomDriver'],
                "location": f"{driver_props['logitude']}, {driver_props['latitude']}", # Format as string
                "telephoneDriver": driver_props['telephoneDriver']
            },
            "prix_base_per_km": price_base,
            "confort": trip_info['confort'],
            "prix_travel": price_travel
        }]
    }
    print(f"Enriched message: {enriched_data}")
    return enriched_data

def publish_to_kafka(**kwargs):
    """Publishes the enriched message to the result Kafka topic."""
    ti = kwargs['ti']
    enriched_data = ti.xcom_pull(task_ids='compute_cost_travel')

    if not enriched_data:
        print("No data received from previous task. Nothing to publish.")
        return

    conf = {'bootstrap.servers': KAFKA_BROKER_URL}
    producer = Producer(conf)

    message_bytes = json.dumps(enriched_data).encode('utf-8')
    producer.produce(DESTINATION_TOPIC, value=message_bytes)
    producer.flush()
    print(f"Published message to '{DESTINATION_TOPIC}'.")