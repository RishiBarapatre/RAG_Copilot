from fastapi import FastAPI
from src.api.routes import router, lifespan

# Initialize the FastAPI app — setup_globals() and the query engine are
# initialized inside the lifespan (see src/api/routes.py), so this module
# is safe to import without triggering any network or model loading.
app = FastAPI(
    title="Production RAG API",
    description="A CPU-optimized Retrieval-Augmented Generation API built with LlamaIndex, Groq, and ChromaDB.",
    version="1.0.0",
    lifespan=lifespan,
)

# Include our API routes
app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)