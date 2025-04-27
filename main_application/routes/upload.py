from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from document_processing import DocumentProcessor
from llm_model import llm_instance
from utils.json_utils import extract_json_from_llm_output
from services.kafka_producer import send_to_kafka
import uuid
import io

router = APIRouter()

@router.post("/")
async def upload_and_process_file(
    file: UploadFile = File(...),
    job_id: str = Form(None),
    application_id: str = Form(None)
):
    """
    Upload and process a resume file.
    
    This endpoint supports both direct processing (original flow) and integration with the 
    job application flow by accepting optional job_id and application_id parameters.
    """
    candidate_id = str(uuid.uuid4())

    try:
        # Read the file content into memory
        file_content = await file.read()
        file_like_object = io.BytesIO(file_content)

        # Process the file content directly
        processor = DocumentProcessor(file_like_object)
        chunks = processor.split_text()
        resume_text = "\n".join(chunks)

        # Use LLM for further processing
        llm_chain = llm_instance.get_chain()
        raw_output = llm_chain.run(resume_text)

        # Extract structured JSON from LLM output
        structured_data = extract_json_from_llm_output(raw_output)

        # Determine which flow to use based on parameters
        if job_id and application_id:
            # Job application flow - send to two Kafka topics
            
            # Send to first Kafka topic (candidate data only)
            candidate_message = {
                "candidate_id": candidate_id,
                "structured_data": structured_data
            }
            await send_to_kafka(candidate_message, topic="candidate_data_topic")
            
            # Send to second Kafka topic (application data with job and candidate info)
            application_message = {
                "application_id": application_id,
                "job_id": job_id,
                "candidate_id": candidate_id,
                "structured_data": structured_data
            }
            await send_to_kafka(application_message, topic="application_resume_topic")
            
            return {
                "filename": file.filename,
                "candidate_id": candidate_id, 
                "application_id": application_id,
                "job_id": job_id,
                "result": structured_data
            }
        else:
            # Original flow - send to processed_resume_topic
            message = {
                "filename": file.filename,
                "structured_data": structured_data,
                "candidateID": candidate_id
            }
            topic = "processed_resume_topic"
            await send_to_kafka(message, topic)
            
            return {
                "filename": file.filename, 
                "candidateID": candidate_id, 
                "result": structured_data
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")