"""
This file is no longer active as we've transitioned to a Kafka-only approach.
The functionality for processing resumes has been moved to kafka_consumer.py.
This file is kept for reference purposes only.
"""

from fastapi import APIRouter

router = APIRouter()

# All previous upload endpoints have been removed as we're now using Kafka exclusively