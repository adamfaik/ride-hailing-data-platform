import json
import time
from confluent_kafka import Producer

# --- Kafka Producer Configuration ---
KAFKA_BROKER_URL = 'localhost:9092'
producer_conf = {
    'bootstrap.servers': KAFKA_BROKER_URL,
}

# The topic we will produce messages to.
TOPIC_NAME = 'topic_source'
DATA_FILE = 'data_projet.json'

# --- Main Execution ---
if __name__ == "__main__":
    # Create a Kafka producer instance
    producer = Producer(producer_conf)
    print(f"Producer started. Sending messages from '{DATA_FILE}' to topic '{TOPIC_NAME}'...")

    # Load the message template from the JSON file
    try:
        with open(DATA_FILE, 'r') as f:
            message_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{DATA_FILE}' was not found. Please make sure it's in the same directory.")
        exit()

    try:
        while True:
            # 1. Convert the loaded dictionary to a JSON string, then encode to bytes
            message_bytes = json.dumps(message_data).encode('utf-8')

            # 2. Produce the message to the Kafka topic
            producer.produce(TOPIC_NAME, value=message_bytes)
            print(f"Sent message: {json.dumps(message_data)}")

            # 3. Flush the producer to ensure the message is sent
            producer.flush()

            # 4. Wait for a few seconds before sending the next message
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nProducer stopped by user.")
    finally:
        # Ensure any remaining messages are sent before exiting
        producer.flush()