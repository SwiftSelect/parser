# from fastapi import APIRouter, UploadFile, File, HTTPException
# from services.s3_service import download_from_s3
# from document_processing import DocumentProcessor
# from llm_model import llm_instance
# from utils.json_utils import extract_json_from_llm_output
# import os
# import shutil

# router = APIRouter()

# @router.post("/")
# async def process_document(file: UploadFile = File(...)):
#     try:
#         # Step 1: Save uploaded file to disk temporarily
#         temp_filename = f"temp_{file.filename}"
#         with open(temp_filename, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # Step 2: Extract text from the PDF
#         processor = DocumentProcessor(temp_filename)
#         chunks = processor.split_text()
#         resume_text = "\n".join([chunk.page_content for chunk in chunks])
        
#         # Step 3: Use LLM for further processing
#         llm_chain = llm_instance.get_chain()
#         raw_output = llm_chain.run(resume_text)
        
#         # Step 4: Extract structured JSON from LLM output
#         structured_resume = extract_json_from_llm_output(raw_output)
        
#         # Step 5: Delete temporary file after processing
#         os.remove(temp_filename)
        
#         return {"filename": file.filename, "result": structured_resume}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, UploadFile, File, HTTPException
from document_processing import DocumentProcessor
from services.kafka_producer import send_to_kafka
from llm_model import llm_instance
from utils.json_utils import extract_json_from_llm_output
import os
import shutil

router = APIRouter()

@router.post("/")
async def process_file(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"

    try:
        # Save the uploaded file locally
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process the file
        processor = DocumentProcessor(temp_file_path)
        chunks = processor.split_text()
        resume_text = "\n".join([chunk.page_content for chunk in chunks])

        # Use LLM for further processing
        llm_chain = llm_instance.get_chain()
        raw_output = llm_chain.run(resume_text)

        # Extract structured JSON from LLM output
        structured_data = extract_json_from_llm_output(raw_output)

        # Send processed data to Kafka
        message = {"filename": file.filename, "structured_data": structured_data}
        topic = "processed_resume_topic"  # Specify the Kafka topic
        await send_to_kafka(message, topic)
        
        # Clean up the temporary file
        os.remove(temp_file_path)

        return {"filename": file.filename, "result": structured_data}
    except Exception as e:
        # Clean up the temporary file in case of an error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")