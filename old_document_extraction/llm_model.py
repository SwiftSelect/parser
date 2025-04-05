from langchain_openai import ChatOpenAI
from config import config

class LLMModel:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=config.OPENAI_API_KEY)
    
    def get_model(self):
        return self.llm

llm_instance = LLMModel()