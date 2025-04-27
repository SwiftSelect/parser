from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import process_router  # Removed upload_router
from services.kafka_consumer import start_consumer, stop_consumer
from services.kafka_producer import start_producer, stop_producer
from utils.logger import logger

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    logger.info("Starting Kafka producer and consumer...")
    await start_producer()  # Start Kafka producer
    await start_consumer()  # Start Kafka consumer
    logger.info("Kafka producer and consumer started.")
    yield  # Application runs here
    logger.info("Shutting down Kafka producer and consumer...")
    await stop_producer()  # Stop Kafka producer
    await stop_consumer()  # Stop Kafka consumer
    logger.info("Kafka producer and consumer stopped.")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Resume Processing API",
    description="An API for processing resumes via Kafka and exposing structured data.",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers - removed upload_router
app.include_router(process_router, prefix="/process", tags=["Process"])

# Add CORS middleware (optional, if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint to check API status."""
    return {"message": "Resume Processing API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)