from fastapi import FastAPI
from src.api.routes import router, lifespan
from src.engine.config import setup_globals

# 1. Setup the global LLM and Embedding models first
setup_globals()

# 2. Initialize the FastAPI app with the lifespan handler
app = FastAPI(
    title="Production RAG API",
    description="A CPU-optimized Retrieval-Augmented Generation API built with LlamaIndex, Groq, and ChromaDB.",
    version="1.0.0",
    lifespan=lifespan,
)

# 3. Include our API routes
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)