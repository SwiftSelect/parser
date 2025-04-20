import boto3
import os
import logging

logger = logging.getLogger(__name__)

# S3 client instance
s3 = boto3.client("s3")

def upload_to_s3(file, key):
    """Upload a file to S3."""
    bucket = os.environ.get("S3_BUCKET", "your-s3-bucket")
    try:
        s3.upload_fileobj(file, bucket, key)
        logger.info(f"Uploaded file to S3: {key}")
    except Exception as e:
        logger.error(f"Error uploading file to S3: {e}")
        raise

def download_from_s3(bucket, key):
    """Download a file from S3 to a temporary location."""
    temp_file = f"/tmp/{key.split('/')[-1]}"
    try:
        s3.download_file(bucket, key, temp_file)
        logger.info(f"Downloaded file from S3: {key}")
        return temp_file
    except Exception as e:
        logger.error(f"Error downloading file from S3: {e}")
        raise

def get_from_s3(key):
    """Retrieve an object from S3."""
    bucket = os.environ.get("S3_BUCKET", "your-s3-bucket")
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        logger.info(f"Retrieved object from S3: {key}")
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        logger.error(f"Error retrieving object from S3: {e}")
        raise