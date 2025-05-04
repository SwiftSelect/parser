from aiokafka import AIOKafkaProducer
import asyncio
import os
import json
import logging
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

logger = logging.getLogger(__name__)

# Define the producer globally
producer = None

async def start_producer():
    """Start the Kafka producer with Confluent Cloud configuration."""
    global producer
    
    # Check if we should use Confluent Cloud or local Kafka
    if os.environ.get("USE_CONFLUENT", "false").lower() == "true":
        ssl_context = ssl.create_default_context()
        # Confluent Cloud configuration
        conf = {
            'bootstrap.servers': os.environ.get("bootstrap.servers", "pkc-921jm.us-east-2.aws.confluent.cloud:9092"),
            'security.protocol': os.environ.get("security.protocol", "SASL_SSL"),
            'sasl.mechanisms': os.environ.get("sasl.mechanisms", "PLAIN"),
            'sasl.username': os.environ.get("sasl.username", os.environ.get("CONFLUENT_KEY")),
            'sasl.password': os.environ.get("sasl.password", os.environ.get("CONFLUENT_SECRET")),
            # Optional: Set client ID if needed for specific operations
            'producer.client.id': os.environ.get("producer.client.id", "ccloud-python-client"),
            'session.timeout.ms': os.environ.get("session.timeout.ms", "45000")
        }
        
        producer = AIOKafkaProducer(
            bootstrap_servers=conf['bootstrap.servers'],
            security_protocol=conf['security.protocol'],
            sasl_mechanism=conf['sasl.mechanisms'],
            sasl_plain_username=conf['sasl.username'],
            sasl_plain_password=conf['sasl.password'],
            client_id=conf['producer.client.id'],
            ssl_context=ssl_context
        )
        logger.info("Starting Confluent Cloud Kafka producer")
    else:
        # Local Kafka configuration
        producer = AIOKafkaProducer(
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        )
        logger.info("Starting local Kafka producer")
    
    await producer.start()
    logger.info("Kafka producer started successfully.")

async def stop_producer():
    """Stop the Kafka producer."""
    global producer
    if producer:
        await producer.stop()
        logger.info("Kafka producer stopped.")

async def send_to_kafka(message: dict, topic: str):
    """Send a message to the specified Kafka topic."""
    if not producer:
        raise RuntimeError("Kafka producer is not started.")
    logger.info(f"Sending message to Kafka topic '{topic}': {message}")
    await producer.send_and_wait(topic, json.dumps(message).encode("utf-8"))