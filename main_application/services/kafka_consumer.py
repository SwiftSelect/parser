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
from utils.supabase_utils import get_resume_signed_url
from dotenv import load_dotenv
import ssl
from supabase import create_client, Client

# Load environment variables from parent directory's .env file for consistent configuration
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

logger = logging.getLogger(__name__)

# Global consumer variable for stopping
consumer = None

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

async def consume():
    """Consume messages from Kafka, process them, and send results to appropriate Kafka topics based on message content."""
    global consumer
    
    # Check if we should use Confluent Cloud or local Kafka
    if os.environ.get("USE_CONFLUENT", "false").lower() == "true":
        ssl_context = ssl.create_default_context()
        # Confluent Cloud configuration
        consumer = AIOKafkaConsumer(
            os.environ.get("KAFKA_RESUME_TOPIC", "candidate_topic"),
            bootstrap_servers=os.environ.get("bootstrap.servers", "pkc-921jm.us-east-2.aws.confluent.cloud:9092"),
            group_id=f"parser_group_{uuid.uuid4()}",
            auto_offset_reset="earliest",
            security_protocol=os.environ.get("security.protocol", "SASL_SSL"),
            sasl_mechanism=os.environ.get("sasl.mechanisms", "PLAIN"),
            sasl_plain_username=os.environ.get("sasl.username", os.environ.get("CONFLUENT_KEY")),
            sasl_plain_password=os.environ.get("sasl.password", os.environ.get("CONFLUENT_SECRET")),
            ssl_context=ssl_context
        )
        logger.info(f"Connecting to Confluent Cloud Kafka at: {os.environ.get('bootstrap.servers')}")
    else:
        # Local Kafka configuration
        consumer = AIOKafkaConsumer(
            os.environ.get("KAFKA_RESUME_TOPIC", "candidate_topic"),
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
            group_id=f"parser_group_{uuid.uuid4()}",
            auto_offset_reset="earliest"
        )
        logger.info(f"Connecting to local Kafka at: {os.environ.get('KAFKA_BOOTSTRAP_SERVERS')}")
    
    await consumer.start()
    
    try:
        async for msg in consumer:
            try:
                # Parse Kafka message
                data = json.loads(msg.value.decode("utf-8"))
                jobId = data.get("jobId")
                applicationId = data.get("applicationId")
                resumeUrl = data.get("resumeUrl")
                candidateId = data.get("candidateId")
                
                # If no candidate_id is provided, generate a new one
                # if not candidate_id:
                #     candidate_id = str(uuid.uuid4())
                    
                logger.info(f"Processing resume from URL: {resumeUrl}, Job ID: {jobId}, Application ID: {applicationId}, Candidate ID: {candidateId}")
                
                file_path = resumeUrl
                
                # Download the resume file using signed URL
                try:
                    logger.info(f"Generating signed URL for file: {file_path}")
                    response_json = get_resume_signed_url(file_path)
                    
                    # Extract signed URL from response
                    response_data = response_json.body.decode('utf-8')
                    signed_url_data = json.loads(response_data)
                    signed_url = signed_url_data.get("signed_url")
                    
                    logger.info(f"Generated signed URL: {signed_url}")
                    
                    # Download file using the signed URL
                    response = requests.get(signed_url)
                    response.raise_for_status()
                    file_like_object = io.BytesIO(response.content)
                    
                    logger.info(f"Successfully downloaded file using signed URL")
                except Exception as e:
                    logger.error(f"Error downloading resume: {str(e)}")
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
                    structuredData = extract_json_from_llm_output(raw_output)
                    
                    logger.info(f"Resume processed successfully for Candidate ID: {candidateId}")
                except Exception as e:
                    logger.error(f"Error processing resume content: {str(e)}")
                    continue

                # Determine which Kafka topic to send to based on message content
                if applicationId and jobId:
                    # If message has application_id and job_id, send to application_resume_topic
                    application_message = {
                        "applicationId": applicationId,
                        "jobId": jobId,
                        "candidateId": candidateId,
                        "structuredData": structuredData
                    }
                    await send_to_kafka(application_message, topic="application_resume_topic")
                    logger.info(f"Sent application data to topic 'application_resume_topic' for Application ID: {applicationId}")
                else:
                    # If message only has candidate_id and resume_url, send to candidate_data_topic
                    candidate_message = {
                        "candidateId": candidateId,
                        "structuredData": structuredData
                    }
                    await send_to_kafka(candidate_message, topic="candidate_data_topic")
                    logger.info(f"Sent candidate data to topic 'candidate_data_topic' for Candidate ID: {candidateId}")
                
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