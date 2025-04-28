from aiokafka import AIOKafkaConsumer
import os
import asyncio
import json
import logging
import uuid
import io
import requests
import boto3
from botocore.client import Config
from services.kafka_producer import send_to_kafka
from document_processing import DocumentProcessor
from llm_model import llm_instance
from utils.json_utils import extract_json_from_llm_output
from dotenv import load_dotenv
# Import Supabase client
from supabase import create_client, Client
load_dotenv()

logger = logging.getLogger(__name__)

# Global consumer variable for stopping
consumer = None

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase_s3_access_key = os.environ.get("SUPABASE_S3_ACCESS_KEY")
supabase = create_client(supabase_url, supabase_key)

# Initialize S3 client for direct S3 access if needed
s3_client = None
if supabase_url and supabase_s3_access_key:
    try:
        # Extract the endpoint from the Supabase URL
        s3_endpoint = supabase_url.replace("https://", "").split(".")[0]
        s3_endpoint = f"https://{s3_endpoint}.supabase.co/storage/v1"
        
        # Initialize the S3 client
        s3_client = boto3.client(
            's3',
            endpoint_url=s3_endpoint,
            aws_access_key_id=supabase_s3_access_key,
            aws_secret_access_key="",  # Not needed for public read-only access
            config=Config(signature_version='s3v4')
        )
        logger.info("S3 client initialized for direct storage access")
    except Exception as e:
        logger.warning(f"Failed to initialize S3 client: {str(e)}")
        s3_client = None

async def consume():
    """Consume messages from Kafka, process them, and send results to appropriate Kafka topics based on message content."""
    global consumer
    consumer = AIOKafkaConsumer(
        os.environ.get("KAFKA_RESUME_TOPIC", "app_job_topic"),
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
                candidate_id = data.get("candidate_id")
                
                # If no candidate_id is provided, generate a new one
                if not candidate_id:
                    candidate_id = str(uuid.uuid4())
                    
                logger.info(f"Processing resume from URL: {resume_url}, Job ID: {job_id}, Application ID: {application_id}, Candidate ID: {candidate_id}")
                
                # Download the resume file from Supabase
                try:
                    file_like_object = None
                    
                    # Parse the Supabase URL to extract bucket and path information
                    if "storage/v1/object/public/" in resume_url:
                        # URL format: https://[project].supabase.co/storage/v1/object/public/[bucket]/[path]
                        parts = resume_url.split("storage/v1/object/public/")
                        if len(parts) > 1:
                            bucket_and_path = parts[1]
                            bucket_parts = bucket_and_path.split("/", 1)
                            
                            if len(bucket_parts) > 1:
                                bucket = bucket_parts[0]
                                file_path = bucket_parts[1]
                                
                                logger.info(f"Downloading file from Supabase bucket: {bucket}, path: {file_path}")
                                
                                # Try primary download method using Supabase client
                                try:
                                    # Download file from Supabase storage
                                    response = supabase.storage.from_(bucket).download(file_path)
                                    
                                    # Create a file-like object from the response
                                    file_like_object = io.BytesIO(response)
                                    filename = file_path.split('/')[-1]
                                    
                                    logger.info(f"Successfully downloaded file from Supabase: {filename}")
                                except Exception as supabase_error:
                                    logger.warning(f"Error using Supabase client: {str(supabase_error)}")
                                    
                                    # Fall back to S3 direct access if available
                                    if s3_client:
                                        logger.info(f"Trying direct S3 access for {bucket}/{file_path}")
                                        try:
                                            # Use S3 client to get the object
                                            s3_response = s3_client.get_object(Bucket=bucket, Key=file_path)
                                            file_content = s3_response['Body'].read()
                                            file_like_object = io.BytesIO(file_content)
                                            filename = file_path.split('/')[-1]
                                            
                                            logger.info(f"Successfully downloaded file using direct S3 access: {filename}")
                                        except Exception as s3_error:
                                            logger.error(f"Error using direct S3 access: {str(s3_error)}")
                                            raise s3_error
                                    else:
                                        # Re-raise the original Supabase error if S3 client isn't available
                                        raise supabase_error
                            else:
                                raise ValueError(f"Invalid Supabase URL format - cannot extract file path: {resume_url}")
                        else:
                            raise ValueError(f"Invalid Supabase URL format: {resume_url}")
                    else:
                        # Fallback to direct HTTP request if not a Supabase URL
                        logger.info(f"URL does not appear to be a Supabase URL, trying direct download: {resume_url}")
                        response = requests.get(resume_url)
                        response.raise_for_status()
                        
                        # Create a file-like object from the response content
                        file_content = response.content
                        file_like_object = io.BytesIO(file_content)
                        
                        # Get the filename from the URL
                        filename = resume_url.split('/')[-1]
                        
                        logger.info(f"Downloaded resume from URL (non-Supabase): {resume_url}")
                        
                    if not file_like_object:
                        raise ValueError("Failed to download file: No download method succeeded")
                        
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
                    
                    logger.info(f"Resume processed successfully for Candidate ID: {candidate_id}")
                except Exception as e:
                    logger.error(f"Error processing resume content: {str(e)}")
                    continue

                # Determine which Kafka topic to send to based on message content
                if application_id and job_id:
                    # If message has application_id and job_id, send to application_resume_topic
                    application_message = {
                        "application_id": application_id,
                        "job_id": job_id,
                        "candidate_id": candidate_id,
                        "structured_data": structured_data
                    }
                    await send_to_kafka(application_message, topic="application_resume_topic")
                    logger.info(f"Sent application data to topic 'application_resume_topic' for Application ID: {application_id}")
                else:
                    # If message only has candidate_id and resume_url, send to candidate_data_topic
                    candidate_message = {
                        "candidate_id": candidate_id,
                        "structured_data": structured_data
                    }
                    await send_to_kafka(candidate_message, topic="candidate_data_topic")
                    logger.info(f"Sent candidate data to topic 'candidate_data_topic' for Candidate ID: {candidate_id}")
                
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