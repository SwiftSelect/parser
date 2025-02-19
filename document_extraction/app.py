# import json
# import sys
# from document_processing import DocumentProcessor
# from llm_model import llm_instance
# from langchain.chains import LLMChain
# from prompt_template import prompt_handler


# def main():
#     if len(sys.argv) < 2:
#         print("Usage: python app.py <PDF_FILE_PATH> [OUTPUT_FILE_PATH]")
#         sys.exit(1)

#     file_path = sys.argv[1]
#     output_file_path = sys.argv[2] if len(sys.argv) > 2 else "output.json"

#     try:
#         # Process the document
#         processor = DocumentProcessor(file_path)
#         chunks = processor.split_text()
#         resume_text = "\n".join([chunk.page_content for chunk in chunks])

#         # Generate structured resume
#         llm_chain = LLMChain(llm=llm_instance.get_model(), prompt=prompt_handler.get_prompt())
#         raw_output = llm_chain.run(resume_text)
        
#         # Improved JSON extraction
#         structured_resume = extract_json_from_llm_output(raw_output)
        
#         # Write the output to a file
#         with open(output_file_path, 'w') as output_file:
#             json.dump(structured_resume, output_file, indent=4, ensure_ascii=False)

#         print(f"Structured resume has been saved to {output_file_path}")

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         sys.exit(1)

# def extract_json_from_llm_output(text):
#     """Extract JSON from LLM output, handling various markdown formats."""
#     # Pattern 1: JSON wrapped in markdown code blocks
#     if "```json" in text:
#         # Extract content between ```json and ```
#         parts = text.split("```json", 1)
#         if len(parts) > 1:
#             json_text = parts[1].split("```", 1)[0].strip()
#         else:
#             json_text = text
#     # Pattern 2: JSON wrapped in plain code blocks
#     elif "```" in text:
#         parts = text.split("```", 1)
#         if len(parts) > 1:
#             json_text = parts[1].split("```", 1)[0].strip()
#         else:
#             json_text = text
#     else:
#         # Assume the whole text is JSON
#         json_text = text.strip()
    
#     try:
#         return json.loads(json_text)
#     except json.JSONDecodeError as e:
#         print(f"JSON parsing error: {e}")
#         print(f"Problematic text: {json_text[:100]}...")
#         raise


# if __name__ == "__main__":
#     main()

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

@app.post("/process-document/")
async def process_document(file: UploadFile = File(...)):
    try:
        temp_filename = f"temp_{file.filename}"
        
        # Save file to disk
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Pass the saved file path to your processing function
        result = DocumentProcessor(temp_filename)  # Example function

        # Delete temp file after processing (optional)
        os.remove(temp_filename)

        return {"filename": file.filename, "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
