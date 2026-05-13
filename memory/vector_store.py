import os
from langchain_community.document_loaders import TextLoader, PDFPlumberLoader
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Use the same model you pulled in your original script
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

def add_to_memory(file_path):
    """Loads a file, splits it, and saves it to the local vector database."""
    if file_path.endswith('.pdf'):
        loader = PDFPlumberLoader(file_path)
    else:
        loader = TextLoader(file_path)

    documents = loader.load()
    
    # persist_directory ensures the data stays on your hard drive
    vector_db = Chroma.from_documents(
        documents,
        embeddings,
        persist_directory="./db"
    )
    print(f"✅ Added {file_path} to StocksPredictor memory.")

def query_memory(question):
    """Searches the local database for relevant context to help the LLM."""
    db = Chroma(persist_directory="./db", embedding_function=embeddings)
    docs = db.similarity_search(question, k=2)
    return " ".join([d.page_content for d in docs])