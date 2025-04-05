# from fastapi import APIRouter, UploadFile, File, HTTPException
# from services.s3_service import upload_to_s3
# from services.kafka_producer import send_to_kafka
# import uuid

# router = APIRouter()

# @router.post("/")
# async def upload_file(file: UploadFile = File(...)):
#     candidate_id = str(uuid.uuid4())
#     key = f"uploads/{candidate_id}/{file.filename}"

#     try:
#         # Upload file to S3
#         upload_to_s3(file.file, key)

#         # Send metadata to Kafka
#         message = {"bucket": "your-s3-bucket", "key": key, "candidate_id": candidate_id}
#         await send_to_kafka(message)

#         return {"message": "File uploaded and Kafka notified", "candidate_id": candidate_id}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# from fastapi import APIRouter, UploadFile, File, HTTPException
# from services.kafka_producer import send_to_kafka
# import uuid
# import os
# import shutil

# router = APIRouter()

# UPLOAD_DIR = "uploads"  # Directory to save uploaded files locally
# os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the directory exists

# @router.post("/")
# async def upload_file(file: UploadFile = File(...)):
#     candidate_id = str(uuid.uuid4())
#     file_path = os.path.join(UPLOAD_DIR, f"{candidate_id}_{file.filename}")

#     try:
#         # Save the file locally
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#         topic = "resume_upload_topic"
#         # Send metadata to Kafka
#         message = {"file_path": file_path, "candidate_id": candidate_id}
#         await send_to_kafka(message, topic)

#         return {"message": "File uploaded and Kafka notified", "candidate_id": candidate_id}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

from fastapi import APIRouter, UploadFile, File, HTTPException
from document_processing import DocumentProcessor
from llm_model import llm_instance
from utils.json_utils import extract_json_from_llm_output
from services.kafka_producer import send_to_kafka
import uuid
import io

router = APIRouter()

@router.post("/")
async def upload_and_process_file(file: UploadFile = File(...)):
    candidate_id = str(uuid.uuid4())

    try:
        # Read the file content into memory
        file_content = await file.read()
        file_like_object = io.BytesIO(file_content)

        # Process the file content directly
        processor = DocumentProcessor(file_like_object)  # Modify DocumentProcessor to accept raw content
        chunks = processor.split_text()
        resume_text = "\n".join(chunks)

        # Use LLM for further processing
        llm_chain = llm_instance.get_chain()
        raw_output = llm_chain.run(resume_text)

        # Extract structured JSON from LLM output
        structured_data = extract_json_from_llm_output(raw_output)

        # Send processed data to Kafka
        message = {"filename": file.filename, "structured_data": structured_data}
        topic = "processed_resume_topic"
        await send_to_kafka(message, topic)

        return {"filename": file.filename, "result": structured_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")