import json
from fastapi import HTTPException

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