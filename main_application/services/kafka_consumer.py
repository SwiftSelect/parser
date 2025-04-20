from aiokafka import AIOKafkaConsumer
import os
import asyncio
import json
import logging
from services.kafka_producer import send_to_kafka
from document_processing import DocumentProcessor
from llm_model import llm_instance
from utils.json_utils import extract_json_from_llm_output
from dotenv import load_dotenv
load_dotenv()
# from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

logger = logging.getLogger(__name__)

# @retry(stop=stop_after_attempt(5), wait=wait_fixed(2), retry_if_exception_type(Exception))
# async def start_consumer_with_retry(consumer):
#     await consumer.start()
#     logger.info("Consumer started successfully")

async def consume():
    """Consume messages from Kafka, process them, and send results to another Kafka topic."""
    consumer = AIOKafkaConsumer(
        os.environ.get("KAFKA_TOPIC", "resume_upload_topic"),
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        group_id=os.environ.get("KAFKA_GROUP_ID", "parser_group"),
        auto_offset_reset="earliest"
    )
    print(f"Connecting to Kafka at: {os.environ.get('KAFKA_BOOTSTRAP_SERVERS')}")
    await consumer.start()
    try:
        async for msg in consumer:
            try:
                # Parse Kafka message
                data = json.loads(msg.value.decode("utf-8"))
                bucket = data["bucket"]
                key = data["key"]
                candidate_id = data["candidate_id"]
                logger.info(f"Processing file for candidate {candidate_id}")

                # Simulate file download (if needed, replace with actual logic)
                temp_filename = f"/tmp/{key.split('/')[-1]}"
                logger.info(f"Simulated download of file: {temp_filename}")

                # Process file
                processor = DocumentProcessor(temp_filename)
                chunks = processor.split_text()
                resume_text = "\n".join([chunk.page_content for chunk in chunks])

                # Use LLM for further processing
                llm_chain = llm_instance.get_chain()
                raw_output = llm_chain.run(resume_text)

                # Extract structured JSON
                structured_data = extract_json_from_llm_output(raw_output)

                # Send processed data to another Kafka topic
                processed_message = {
                    "candidate_id": candidate_id,
                    "structured_data": structured_data
                }
                await send_to_kafka(processed_message, topic="processed_resume_topic")

                logger.info(f"Processed data for candidate {candidate_id} sent to Kafka topic 'processed_resume_topic'")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    finally:
        await consumer.stop()

async def start_consumer():
    """Start the Kafka consumer."""
    asyncio.create_task(consume())
    
async def stop_consumer():
    """Stop the Kafka consumer."""
    global consumer
    if consumer:
        await consumer.stop()
        logger.info("Kafka consumer stopped.")