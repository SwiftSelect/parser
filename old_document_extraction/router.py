from fastapi import APIRouter
from schema import Message
from config import loop, KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, KAFKA_CONSUMER_GROUP
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

router = APIRouter()
# @route.post(/)