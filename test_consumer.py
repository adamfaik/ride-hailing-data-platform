from confluent_kafka import Consumer

# --- Kafka Consumer Configuration ---
KAFKA_BROKER_URL = 'localhost:9092'
consumer_conf = {
    'bootstrap.servers': KAFKA_BROKER_URL,
    'group.id': 'my-test-consumer-group', # A unique name for the consumer group
    'auto.offset.reset': 'earliest' # Start reading from the beginning of the topic
}

TOPIC_NAME = 'topic_source'

# --- Main Execution ---
if __name__ == "__main__":
    consumer = Consumer(consumer_conf)
    consumer.subscribe([TOPIC_NAME])
    print(f"Consumer started. Listening to topic '{TOPIC_NAME}'...")

    try:
        while True:
            # Poll for new messages
            msg = consumer.poll(1.0) # Timeout of 1 second

            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            # Print the received message
            print(f"Received message: {msg.value().decode('utf-8')}")

    except KeyboardInterrupt:
        print("\nConsumer stopped by user.")
    finally:
        # Cleanly close the consumer
        consumer.close()