# from langchain_openai import ChatOpenAI
# from config import config

# class LLMModel:
#     def __init__(self):
#         self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=config.OPENAI_API_KEY)
    
#     def get_model(self):
#         return self.llm

# llm_instance = LLMModel()

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from prompt_template import prompt_handler  # Import the prompt handler
from config import config

class LLMModel:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=config.OPENAI_API_KEY)
    
    def get_model(self):
        return self.llm

    def get_chain(self):
        # Reuse the prompt from prompt_template.py
        prompt = prompt_handler.get_prompt()
        # Create and return an LLMChain
        return LLMChain(llm=self.llm, prompt=prompt)

llm_instance = LLMModel()