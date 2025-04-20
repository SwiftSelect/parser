# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter

# class DocumentProcessor:
#     def __init__(self, file_path):
#         self.file_path = file_path
#         self.pages = self.load_pdf()

#     def load_pdf(self):
#         loader = PyPDFLoader(self.file_path)
#         return loader.load()
    
#     def split_text(self, chunk_size=1500, chunk_overlap=200):
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len, separators=["\n\n", "\n", " "])
#         return text_splitter.split_documents(self.pages)

from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, file_content):
        self.file_content = file_content
        self.pages = self.load_pdf()

    def load_pdf(self):
        # Use PyPDF2 to read the PDF from raw content
        reader = PdfReader(self.file_content)
        return [page.extract_text() for page in reader.pages]

    def split_text(self, chunk_size=1500, chunk_overlap=200):
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len, separators=["\n\n", "\n", " "]
        )
        return text_splitter.split_text("\n".join(self.pages))