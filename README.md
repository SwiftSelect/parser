# SwiftSelect Resume Processing API

This repository contains a FastAPI-based application designed to process resumes and extract structured data in JSON format. The application uses Kafka for asynchronous messaging and integrates with Supabase for storage.

---

## Features

- **Asynchronous Resume Processing**: Consumes resume URLs from Kafka topics and processes them
- **Structured Data Extraction**: Uses LLM to extract structured information such as name, contact details, education, skills, and experience from resumes
- **Kafka Integration**: Consumes from candidate topics and publishes processed data to relevant downstream topics
- **Containerized Architecture**: Fully dockerized application with Confluent Kafka integration
- **Supabase Storage**: Fetches resumes from Supabase using signed URLs

---

## Prerequisites

1. **Docker and Docker Compose**: For containerizing the application and its dependencies
2. **OpenAI API Key**: For LLM-based resume parsing
3. **Confluent Cloud Account** (optional): For cloud-based Kafka or use local Kafka
4. **Supabase Account**: For storage functionality

---

## Project Structure

```
parser/
├── main_application/
│   ├── app.py                # Main FastAPI application with Kafka consumer/producer
│   ├── services/
│   │   ├── kafka_consumer.py # Consumes resume URLs and processes them
│   │   └── kafka_producer.py # Sends processed data to downstream topics
│   ├── utils/
│   │   ├── json_utils.py     # Utilities for JSON processing
│   │   ├── supabase_utils.py # Supabase integration for storage
│   │   └── logger.py         # Logging configuration
│   ├── document_processing.py # Resume processing logic
│   ├── llm_model.py          # LLM integration for resume parsing
│   └── prompt_template.py    # Prompt templates for LLM
├── Dockerfile                # Container definition
├── docker-compose.yml        # Docker configuration for all services
└── requirements.txt          # Python dependencies
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/swiftselect-parser.git
cd swiftselect-parser
```

### 2. Set Up Environment Variables

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your-openai-api-key
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_RESUME_TOPIC=candidate_topic
KAFKA_CANDIDATE_TOPIC=candidate_data_topic
KAFKA_APPLICATION_TOPIC=application_resume_topic
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-key
USE_CONFLUENT=false  # Set to true if using Confluent Cloud
```

For Confluent Cloud usage, add these additional variables:

```
bootstrap.servers=your-confluent-bootstrap-servers
sasl.username=your-confluent-key
sasl.password=your-confluent-secret
```

### 3. Build and Run with Docker

```bash
docker-compose up -d
```

This will start:

- The FastAPI application (parser-api)
- Kafka broker and Zookeeper (if using local Kafka)
- Kafdrop UI for monitoring Kafka topics

---

## Running the Application

### 1. Check if the API is Running

Access the API status endpoint at http://localhost:8000/

You should see:

```json
{ "message": "Resume Processing API is running!" }
```

### 2. Monitor Kafka Processing

The application consumes messages from the `candidate_topic` and processes resumes. Depending on the message structure, it will:

- For candidate messages: Process and send to `candidate_data_topic`
- For application messages: Process and send to `application_resume_topic`

### 3. Using Kafdrop to Monitor Topics

Kafdrop UI is available at http://localhost:9000 for monitoring Kafka topics and messages.

### Example Processed Resume Structure

```json
{
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
    "programming_databases": ["Python", "C/C++", "SQL"],
    "frameworks": ["FastAPI", "Django"],
    "ml_genai": ["TensorFlow", "PyTorch"],
    "devops_tools": ["Docker", "Kubernetes"]
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
```

## Development Notes

### Architecture

- The application is now fully Kafka-based with no REST endpoints for uploads
- Resume files are stored in Supabase and accessed via signed URLs
- The system is designed to work with both local Kafka and Confluent Cloud

### Docker Image

The Docker image is available on Docker Hub:

```
shreyaskulkarni/swiftselect-parser-api:latest
```

You can also build it yourself:

```bash
docker build -t yourusername/swiftselect-parser-api:latest -f Dockerfile ..
```

### Future Enhancements

- Enhanced error handling and dead-letter queue for failed messages
- Performance optimizations for LLM processing
- Metrics and monitoring integration
- Support for additional file formats and languages

### License

This project is licensed under the MIT License. See the LICENSE file for details.
