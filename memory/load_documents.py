import os
from langchain_community.document_loaders import TextLoader, PDFPlumberLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from config.logger_util import logger
import langchain
langchain.debug = True  

logger.info(f"Memory File Called")

embeddings = OllamaEmbeddings(model="nomic-embed-text")

def add_to_memory(file_path="../data/sample.pdf"):
    logger.info(f"Adding {file_path} to memory.")
    if file_path.endswith('.pdf'):
        loader = PDFPlumberLoader(file_path)
    else:
        loader = TextLoader(file_path)

    documents = loader.load()
    vector_db = Chroma.from_documents(
        documents,
        embeddings,
        persist_directory="./data/storage"
    )
    logger.info(f"Added {file_path} to StocksPredictor memory.")

def query_memory(question):
    db = Chroma(persist_directory="./data/storage", embedding_function=embeddings)
    docs = db.similarity_search(question, k=2)
    logger.info(f"Querying memory with: {question}")
    return " ".join([d.page_content for d in docs])