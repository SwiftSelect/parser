# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set working directory to match your project structure
WORKDIR /app/parser/main_application

# Copy requirements file first for better caching
COPY parser/requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# # Copy the .env file
# COPY parser/.env /app/parser/.env

# Copy the application code
COPY parser/main_application /app/parser/main_application/

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]