import asyncio

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "kafka"
KAFKA_CONSUMER_GROUP = "group-id"
loop = asyncio.get_event_loop()