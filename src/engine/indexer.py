import os
import chromadb
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import MarkdownNodeParser
from src.engine.config import setup_globals

def build_index(data_dir: str = "./data", db_path: str = "./chroma_db"):
    """Reads documents, chunks them, and builds a local vector database."""

    setup_globals()
    
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        print(f"Data directory '{data_dir}' is empty or does not exist.")
        return None

    print(f"Loading documents from {data_dir}...")
    documents = SimpleDirectoryReader(data_dir).load_data()

    print("Parsing documents based on Markdown structure...")
    parser = MarkdownNodeParser()
    nodes = parser.get_nodes_from_documents(documents)

    print("Initializing local ChromaDB...")
    # Initialize the local persistent Chroma client
    db = chromadb.PersistentClient(path=db_path)
    chroma_collection = db.get_or_create_collection("tech_docs")

    # Connect ChromaDB to LlamaIndex
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Embedding nodes and building index (this might take a minute on CPU)...")
    index = VectorStoreIndex(nodes, storage_context=storage_context)
    
    print("Indexing complete!")
    return index