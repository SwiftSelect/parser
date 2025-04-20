from fastapi import FastAPI, File, UploadFile, HTTPException
import json
from document_processing import DocumentProcessor
from llm_model import llm_instance
from langchain.chains import LLMChain
from prompt_template import prompt_handler
import uvicorn
import os
import shutil

app = FastAPI()

def extract_json_from_llm_output(text: str):
    """Extract JSON from LLM output, handling various markdown formats."""
    if "```json" in text:
        parts = text.split("```json", 1)
        json_text = parts[1].split("```", 1)[0].strip() if len(parts) > 1 else text
    elif "```" in text:
        parts = text.split("```", 1)
        json_text = parts[1].split("```", 1)[0].strip() if len(parts) > 1 else text
    else:
        json_text = text.strip()
    
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON parsing error: {str(e)}")

@app.get("/")
async def read_root():
    return {"message": "API is running!"}


@app.post("/process-document/")
async def process_document(file: UploadFile = File(...)):
    try:
        # Step 1: Save uploaded file to disk temporarily
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 2: Extract text from the PDF
        processor = DocumentProcessor(temp_filename)
        chunks = processor.split_text()
        resume_text = "\n".join([chunk.page_content for chunk in chunks])
        
        # Step 3: Use LLM for further processing
        llm_chain = LLMChain(llm=llm_instance.get_model(), prompt=prompt_handler.get_prompt())
        raw_output = llm_chain.run(resume_text)
        
        # Step 4: Extract structured JSON from LLM output
        structured_resume = extract_json_from_llm_output(raw_output)
        
        # Step 5: Delete temporary file after processing (optional)
        os.remove(temp_filename)
        
        return {"filename": file.filename, "result": structured_resume}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)

# from fastapi import FastAPI, UploadFile, File
# import boto3
# from kafka import KafkaProducer
# from aiokafka import AIOKafkaConsumer
# import asyncio
# import json
# import uuid
# import os
# import tempfile
# import logging
# from document_processing import DocumentProcessor
# from llm_model import llm_instance
# from langchain.chains import LLMChain
# from prompt_template import prompt_handler
# from contextlib import asynccontextmanager
# import os

# # Set up FastAPI app
# # app = FastAPI()

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # AWS S3 client (configure with your credentials or IAM role)
# s3 = boto3.client("s3")

# # Kafka Producer for sending messages
# producer = KafkaProducer(bootstrap_servers="localhost:9092")  # Replace with your Kafka broker address

# # Configurations (ideally from environment variables)
# # S3_BUCKET = "your-s3-bucket"  # Replace with your bucket name
# # KAFKA_TOPIC = "resume_upload_topic"
# # KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"  # Replace with your Kafka broker address
# # KAFKA_GROUP_ID = "parser_group"

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup: Start the Kafka consumer
#     consumer_task = asyncio.create_task(consume())
#     yield  # Application runs here
#     # Shutdown: Cancel the consumer task
#     consumer_task.cancel()
#     try:
#         await consumer_task
#     except asyncio.CancelledError:
#         logger.info("Kafka consumer task cancelled during shutdown")
        
# app = FastAPI(lifespan=lifespan)

# # Upload endpoint
# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     # Generate a unique candidate_id
#     candidate_id = str(uuid.uuid4())
    
#     # Define S3 storage key
#     key = f"uploads/{candidate_id}/{file.filename}"
    
#     try:
#         # Upload the file to S3
#         s3.upload_fileobj(file.file, os.environ.get("S3_BUCKET"), key)
#         logger.info(f"Uploaded file to S3: {key}")
        
#         # Send message to Kafka
#         message = {
#             "bucket": os.environ.get("S3_BUCKET"),
#             "key": key,
#             "candidate_id": candidate_id
#         }
#         producer.send(os.environ.get("KAFKA_TOPIC"), json.dumps(message).encode("utf-8"))
#         logger.info(f"Sent Kafka message for candidate {candidate_id}")
        
#         return {"message": "File uploaded and Kafka notified", "candidate_id": candidate_id}
#     except Exception as e:
#         logger.error(f"Error in upload: {e}")
#         return {"message": f"Upload failed: {str(e)}"}

# # Kafka consumer for parsing
# async def consume():
#     consumer = AIOKafkaConsumer(
#         os.environ.get("KAFKA_TOPIC"),
#         bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS"),
#         group_id=os.environ.get("KAFKA_GROUP_ID"),
#         auto_offset_reset="earliest",
#         enable_auto_commit=False
#     )
#     await consumer.start()
#     try:
#         async for msg in consumer:
#             try:
#                 # Parse Kafka message
#                 data = json.loads(msg.value.decode("utf-8"))
#                 bucket = data["bucket"]
#                 key = data["key"]
#                 candidate_id = data["candidate_id"]
#                 logger.info(f"Processing file for candidate {candidate_id}")

#                 # Download file from S3 to a temporary location
#                 with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#                     s3.download_file(bucket, key, tmp_file.name)
#                     temp_filename = tmp_file.name

#                 try:
#                     # Step 1: Extract text from the PDF
#                     processor = DocumentProcessor(temp_filename)
#                     chunks = processor.split_text()
#                     resume_text = "\n".join([chunk.page_content for chunk in chunks])

#                     # Step 2: Use LLM for further processing
#                     llm_chain = LLMChain(llm=llm_instance.get_model(), prompt=prompt_handler.get_prompt())
#                     raw_output = llm_chain.run(resume_text)

#                     # Step 3: Extract structured JSON from LLM output
#                     structured_resume = extract_json_from_llm_output(raw_output)

#                     # Step 4: Store the result in S3
#                     result_key = f"processed/{candidate_id}.json"
#                     s3.put_object(
#                         Bucket=os.environ.get("S3_BUCKET"),
#                         Key=result_key,
#                         Body=json.dumps(structured_resume).encode("utf-8")
#                     )
#                     logger.info(f"Stored parsed result for candidate {candidate_id} at {result_key}")

#                     # Commit the Kafka offset
#                     await consumer.commit()

#                 finally:
#                     # Clean up temporary file
#                     os.remove(temp_filename)

#             except Exception as e:
#                 logger.error(f"Error processing message: {e}")
#     finally:
#         await consumer.stop()

# # Helper function to extract JSON from LLM output
# def extract_json_from_llm_output(text: str):
#     """Extract JSON from LLM output, handling various markdown formats."""
#     if "```json" in text:
#         parts = text.split("```json", 1)
#         json_text = parts[1].split("```", 1)[0].strip() if len(parts) > 1 else text
#     elif "```" in text:
#         parts = text.split("```", 1)
#         json_text = parts[1].split("```", 1)[0].strip() if len(parts) > 1 else text
#     else:
#         json_text = text.strip()
    
#     try:
#         return json.loads(json_text)
#     except json.JSONDecodeError as e:
#         logger.error(f"JSON parsing error: {str(e)}")
#         raise

# # FastAPI startup event to run the Kafka consumer


# @app.get("/")
# def read_root():
#     return {"message": "API is running!"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=5000)