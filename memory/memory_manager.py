from langchain_community.document_loaders import TextLoader, PDFPlumberLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from config.settings import EMBED_MODEL, VECTOR_DB_DIR

embeddings = OllamaEmbeddings(model=EMBED_MODEL)


def add_to_memory(file_path):
    if file_path.endswith('.pdf'):
        loader = PDFPlumberLoader(file_path)
    else:
        loader = TextLoader(file_path)

    documents = loader.load()

    Chroma.from_documents(
        documents,
        embeddings,
        persist_directory=VECTOR_DB_DIR
    )

    print(f"Added {file_path} to memory")



def query_memory(question):
    db = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings
    )

    docs = db.similarity_search(question, k=2)

    return " ".join([d.page_content for d in docs])