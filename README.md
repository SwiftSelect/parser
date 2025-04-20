# Resume Processing API

This repository contains a FastAPI-based application designed to upload resumes, process them, and extract structured data in JSON format. The application integrates Kafka for asynchronous messaging and supports file uploads via the `/upload` endpoint.

---

## Features

- **File Upload and Processing**: Upload resumes (e.g., PDFs or text files) and process them in a single step.
- **Structured Data Extraction**: Extracts structured information such as name, contact details, education, skills, and experience from resumes.
- **Kafka Integration**: Sends processed data to a Kafka topic for further downstream processing.
- **Scalable Architecture**: Built with FastAPI and Kafka for high performance and scalability.

---

## Prerequisites

1. **Docker**: Ensure Docker is installed for running Kafka and Zookeeper.
2. **Python**: Install Python 3.8+.
3. **Dependencies**: Install the required Python packages listed in `requirements.txt`.

---

## Project Structure

```
parser/
├── main_application/
│   ├── app.py                # Main FastAPI application
│   ├── routes/
│   │   └── upload.py         # Upload and processing endpoint
│   ├── services/             # Kafka producer and consumer services
│   ├── utils/                # Utility functions (e.g., JSON extraction, logging)
│   ├── models/               # Pydantic models for structured data
│   ├── config.py             # Configuration file for environment variables
├── docker-compose.yml        # Docker configuration for Kafka and Zookeeper
├── requirements.txt          # Python dependencies
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/resume-processing-api.git
cd resume-processing-api
```

### 2. Start Kafka Using Docker

Run the following command to start Kafka and Zookeeper:

```bash
docker-compose up -d
```

### 3. Install Python Dependencies

Create a virtual environment and install the dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r [requirements.txt]
```

---

## Running the Application

### 1. Start the FastAPI Server

Run the following command to start the application:

```bash
python app.py
```

The server will start at http://127.0.0.1:8000.

### 2. Test the /upload Endpoint

Use Postman or curl to test the /upload endpoint.

### Example response

```
{
  "filename": "resume.pdf",
  "result": {
    "name": "John Doe",
    "contact": {
      "phone": "+1-123-456-7890",
      "email": "johndoe@example.com",
      "linkedin": "https://linkedin.com/in/johndoe",
      "github": "https://github.com/johndoe"
    },
    "education": [
      {
        "degree": "Master of Science",
        "field": "Computer Engineering",
        "university": "San Jose State University",
        "start_date": "Aug. 2023",
        "end_date": "May 2025"
      }
    ],
    "technical_skills": {
      "languages": ["Python", "C/C++", "SQL"],
      "tools": ["TensorFlow", "PyTorch", "Docker"]
    },
    "experience": [
      {
        "title": "Deep Learning Project Assistant",
        "company": "San Jose State University",
        "location": "San Jose, CA",
        "start_date": "Aug. 2024",
        "end_date": "Present",
        "responsibilities": [
          "Utilizing Semantic Textual Similarity (STS) and pre-trained generative models to build an AI-driven recruitment platform.",
          "Integrating real-time data streams using Kafka for asynchronous processing."
        ]
      }
    ]
  }
}
```

### Key Components

/upload Endpoint
Method: POST
Description: Handles file uploads and processes the content to extract structured data.
Input: A file (e.g., PDF or text file).
Output: JSON containing structured resume data.

### Kafka Integration

Producer: Sends processed resume data to the processed_resume_topic.
Consumer: Can be extended to consume messages for downstream processing.

### Development Notes

The application is tested for PDF files but can be extended to support other formats.
The /process endpoint is not used, as the /upload endpoint handles both uploading and processing.
Ensure Kafka is running before starting the application.

### Future Enhancements

Add support for additional file formats (e.g., DOCX).
Implement authentication and authorization for secure API access.
Extend Kafka consumer functionality for real-time analytics.

### License

This project is licensed under the MIT License. See the LICENSE file for details.
