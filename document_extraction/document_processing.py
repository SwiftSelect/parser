from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pages = self.load_pdf()

    def load_pdf(self):
        loader = PyPDFLoader(self.file_path)
        return loader.load()
    
    def split_text(self, chunk_size=1500, chunk_overlap=200):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len, separators=["\n\n", "\n", " "])
        return text_splitter.split_documents(self.pages)