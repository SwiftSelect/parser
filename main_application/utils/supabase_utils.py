"""
Utility functions for Supabase interactions.
"""

import os
import logging
from typing import Dict
from fastapi.responses import JSONResponse
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def get_resume_signed_url(file_path: str):
    try:
        signed_url = supabase.storage.from_("resumes").create_signed_url(
            file_path,
            3600  # URL valid for 1 hour
        )
        logger.info(f"Generated signed URL for resume: {file_path}")
        print(f"url: {signed_url}")
        return JSONResponse({
            "signed_url": signed_url["signedURL"]
        })
    except Exception as e:
        logger.error(f"Error creating signed URL for {file_path}: {str(e)}")
        raise