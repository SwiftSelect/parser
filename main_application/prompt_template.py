from langchain.prompts import PromptTemplate

class PromptHandler:
    def __init__(self):
        self.prompt_template = PromptTemplate(
            input_variables=["resume_text"],
            template="""You are an AI assistant that extracts information from the uploaded resume and gives it a clean JSON format.
            You are given a resume text and your task is to extract the following information and format it into a JSON structure.
            Given the following resume text, format it into a clean JSON structure:
            
            RESUME TEXT:
            {resume_text}
            
            OUTPUT JSON FORMAT:
            {{
              "name": "Candidate Name",
              "contact": {{
                "phone": "+1-XXX-XXX-XXXX",
                "email": "example@email.com",
                "linkedin": "LinkedIn Profile URL",
                "github": "GitHub Profile URL"
              }},
              "education": [
                {{
                  "degree": "Master of Science",
                  "field": "Computer Engineering",
                  "university": "San Jose State University",
                  "start_date": "Aug. 2023",
                  "end_date": "May 2025"
                }}
              ],
              "technical_skills": {{
                "languages": ["Python", "C/C++", "SQL"],
                "tools": ["TensorFlow", "PyTorch", "Docker"]
              }},
              "experience": [
                {{
                  "title": "Deep Learning Project Assistant",
                  "company": "San Jose State University",
                  "location": "San Jose, CA",
                  "start_date": "Aug. 2024",
                  "end_date": "Present",
                  "responsibilities": [
                    "Utilizing Semantic Textual Similarity (STS), zero-shot (all-MiniLM-L6-v2) and pre-trained generative models (BERT, Llama 3.1) to build AI-driven recruitment platform for candidate-job matching",
                    "Optimizing low-latency inference models deployed on AWS SageMaker, integrating Milvus vector database with FastAPI and AWS Elastic Kubernetes Services, achieving sub-100ms response time",
                    "Integrating real-time data streams using Kafka and EventHub to enable asynchronous processing and efficient data ingestion and extracted structured data using LangChain and OpenAI"
                  ]
                }}
              ],
              "projects": [
                {{
                  "title": "Brain MRI Classifier",
                  "start_date": "Jan. 2025",
                  "end_date": "Feb. 2025",
                  "description": "Developed an end-to-end deep learning pipeline for multi-class brain MRI image classification, achieving an accuracy of 97% using VGGNet and transfer learning along with MLOps tools like DVC and GitHub Actions. Deployed the model on AWS using Docker and CI/CD pipelines, enabling scalable real-time image classification with seamless data access from AWS S3, processing over 7,000 MRI images efficiently.",
                  "technologies": ["VGGNet", "MLOps", "AWS S3"]
                }}
              ]
            }}
            
            Ensure the output strictly follows this JSON format. 
            DO not summarize or paraphrase the resume text.
            If you cannot extract certain fields, leave them as null or empty.
            If the resume text is empty or not in English, return an empty JSON object.
            Fields will subheadings and each subheadings might have multi-line bullet points. 
            """
        )
    
    def get_prompt(self):
        return self.prompt_template

prompt_handler = PromptHandler()