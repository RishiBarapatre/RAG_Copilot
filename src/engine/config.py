import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def setup_globals(dotenv_path: str = None):
    """Initializes and sets the global LLM and Embedding models.
    
    Args:
        dotenv_path: Optional absolute path to a .env file. When None, 
                     python-dotenv searches from the current working directory.
    """
    load_dotenv(dotenv_path=dotenv_path)
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not set in the environment.")

    # 1. Set the LLM (Groq)
    # Use a model available on your Groq free tier.
    # Check available models: https://console.groq.com/docs/models
    # or via: GET https://api.groq.com/openai/v1/models
    Settings.llm = Groq(model="openai/gpt-oss-20b", api_key=groq_api_key)

    # 2. Set the Embedding Model (Local CPU)
    # all-MiniLM-L6-v2 is ultra-lightweight and runs perfectly without a GPU.
    Settings.embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
    
    print("Global LLM and Embedding models configured successfully.")