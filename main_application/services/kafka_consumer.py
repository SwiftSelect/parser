from aiokafka import AIOKafkaConsumer
import os
import asyncio
import json
import logging
import uuid
import io
import requests
from services.kafka_producer import send_to_kafka
from document_processing import DocumentProcessor
from llm_model import llm_instance
from utils.json_utils import extract_json_from_llm_output
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# Global consumer variable for stopping
consumer = None

async def consume():
    """Consume messages from Kafka, process them, and send results to two different Kafka topics."""
    global consumer
    consumer = AIOKafkaConsumer(
        os.environ.get("KAFKA_RESUME_TOPIC", "resume_ingestion_topic"),
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
                job_id = data.get("job_id")
                application_id = data.get("application_id")
                resume_url = data.get("resume_url")
                
                logger.info(f"Processing resume from URL: {resume_url}, Job ID: {job_id}, Application ID: {application_id}")

                # Generate a unique candidate ID
                candidate_id = str(uuid.uuid4())
                
                # Download the resume file from the URL
                try:
                    response = requests.get(resume_url)
                    response.raise_for_status()
                    
                    # Create a file-like object from the response content
                    file_content = response.content
                    file_like_object = io.BytesIO(file_content)
                    
                    # Get the filename from the URL
                    filename = resume_url.split('/')[-1]
                    
                    logger.info(f"Downloaded resume from URL: {resume_url}")
                except Exception as e:
                    logger.error(f"Error downloading resume from URL: {resume_url}, Error: {str(e)}")
                    continue

                # Process the file content directly
                try:
                    processor = DocumentProcessor(file_like_object)
                    chunks = processor.split_text()
                    resume_text = "\n".join(chunks)
                    
                    # Use LLM for further processing
                    llm_chain = llm_instance.get_chain()
                    raw_output = llm_chain.run(resume_text)
                    
                    # Extract structured JSON from LLM output
                    structured_data = extract_json_from_llm_output(raw_output)
                    
                    logger.info(f"Resume processed successfully for Application ID: {application_id}")
                except Exception as e:
                    logger.error(f"Error processing resume content: {str(e)}")
                    continue

                # Send to first Kafka topic (candidate data only)
                candidate_message = {
                    "candidate_id": candidate_id,
                    "structured_data": structured_data
                }
                await send_to_kafka(candidate_message, topic="candidate_data_topic")
                logger.info(f"Sent candidate data to topic 'candidate_data_topic' for Candidate ID: {candidate_id}")

                # Send to second Kafka topic (application data with job and candidate info)
                application_message = {
                    "application_id": application_id,
                    "job_id": job_id,
                    "candidate_id": candidate_id,
                    "structured_data": structured_data
                }
                await send_to_kafka(application_message, topic="application_resume_topic")
                logger.info(f"Sent application data to topic 'application_resume_topic' for Application ID: {application_id}")
                
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
    finally:
        await consumer.stop()

async def start_consumer():
    """Start the Kafka consumer."""
    asyncio.create_task(consume())
    logger.info("Kafka consumer started and listening for resume data")
    
async def stop_consumer():
    """Stop the Kafka consumer."""
    global consumer
    if consumer:
        await consumer.stop()
        logger.info("Kafka consumer stopped.")