import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.postprocessor.flashrank_rerank import FlashRankRerank

def get_query_engine(db_path: str = "./chroma_db"):
    """Loads the database and creates a query engine with a CPU reranker."""
    
    # 1. Load the existing ChromaDB collection
    db = chromadb.PersistentClient(path=db_path)
    chroma_collection = db.get_or_create_collection("tech_docs")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # 2. Load the index from the vector store
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    
    # 3. Setup CPU-friendly FlashRank Reranker
    # We fetch the top 15 results from vector search, then rerank to the best 3
    reranker = FlashRankRerank(top_n=3, model="ms-marco-TinyBERT-L-2-v2")
    
    # 4. Build and return the query engine
    query_engine = index.as_query_engine(
        similarity_top_k=15,
        node_postprocessors=[reranker]
    )
    
    return query_engine