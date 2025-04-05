from aiokafka import AIOKafkaProducer
import asyncio
import os
import json
import logging

logger = logging.getLogger(__name__)

# Kafka producer instance
# producer = AIOKafkaProducer(
#     # loop=asyncio.get_event_loop(),
#     bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
# )

producer = None  # Define the producer globally

async def start_producer():
    """Start the Kafka producer."""
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    )
    await producer.start()
    logger.info("Kafka producer started.")

async def stop_producer():
    """Stop the Kafka producer."""
    global producer
    if producer:
        await producer.stop()
        logger.info("Kafka producer stopped.")

# async def send_to_kafka(message: dict, topic: str):
#     """Send a message to the specified Kafka topic."""
#     await producer.start()
#     try:
#         logger.info(f"Sending message to Kafka topic '{topic}': {message}")
#         await producer.send_and_wait(topic, json.dumps(message).encode("utf-8"))
#     finally:
#         await producer.stop()

async def send_to_kafka(message: dict, topic: str):
    """Send a message to the specified Kafka topic."""
    if not producer:
        raise RuntimeError("Kafka producer is not started.")
    logger.info(f"Sending message to Kafka topic '{topic}': {message}")
    await producer.send_and_wait(topic, json.dumps(message).encode("utf-8"))