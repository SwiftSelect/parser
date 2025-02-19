from langchain.prompts import PromptTemplate

class PromptHandler:
    def __init__(self):
        self.prompt_template = PromptTemplate(
            input_variables=["resume_text"],
            template="""You are an AI assistant that extracts structured information from raw resume text.
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
                    "Used zero-shot models (all-MiniLM-L6-v2) and pre-trained generative models to improve resume parsing.",
                    "Developed an AI chatbot using Nvidia embedding models, Milvus, and Gradio for real-time resume queries."
                  ]
                }}
              ],
              "projects": [
                {{
                  "title": "Brain MRI Classifier",
                  "start_date": "Jan. 2025",
                  "end_date": "Feb. 2025",
                  "description": "Developed an end-to-end deep learning pipeline for multi-class brain MRI classification.",
                  "technologies": ["VGGNet", "MLOps", "AWS S3"]
                }}
              ]
            }}
            
            Ensure the output strictly follows this JSON format. 
            """
        )
    
    def get_prompt(self):
        return self.prompt_template

prompt_handler = PromptHandler()