from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from src.engine.retriever import get_query_engine

router = APIRouter()
query_engine = None


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and clean up on shutdown."""
    global query_engine
    try:
        query_engine = get_query_engine()
        print("Query Engine loaded successfully.")
    except Exception as e:
        print(
            f"Warning: Could not load query engine on startup. "
            f"Did you run the indexer first? Error: {e}"
        )
    yield
    # Shutdown: nothing to clean up for ChromaDB PersistentClient


@router.post("/ask", response_model=QueryResponse)
async def ask_question(req: QueryRequest):
    if not query_engine:
        raise HTTPException(
            status_code=503,
            detail="Query engine is not initialized. Please run the indexer first."
        )

    # Execute the RAG pipeline
    response = query_engine.query(req.question)

    # Extract metadata for citations
    sources = [node.metadata for node in response.source_nodes]

    return QueryResponse(
        answer=str(response),
        sources=sources
    )