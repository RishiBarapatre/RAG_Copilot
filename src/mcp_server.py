import sys
import os

# Force Python to recognize the root 'rag-copilot' folder so 'src' imports work
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))
sys.path.insert(0, _PROJECT_ROOT)

# Derive absolute paths so the server works regardless of the working directory
# that an MCP client (e.g. Claude Desktop, Cursor) launches it from.
_DOTENV_PATH = os.path.join(_PROJECT_ROOT, ".env")
_CHROMA_DB_PATH = os.path.join(_PROJECT_ROOT, "chroma_db")

from fastmcp import FastMCP
from src.engine.config import setup_globals
from src.engine.retriever import get_query_engine

# 1. Initialize the MCP Server
mcp = FastMCP("React RAG Copilot")

# Global state for the query engine
query_engine = None

# 2. Expose the Python function as an MCP Tool
@mcp.tool()
def query_react_docs(question: str) -> str:
    """
    Queries the local React documentation RAG pipeline.
    Use this tool to find accurate, cited answers about React features like useState, hooks, etc.
    """
    global query_engine

    # Lazy load the query engine on the first request
    if query_engine is None:
        setup_globals(dotenv_path=_DOTENV_PATH)
        query_engine = get_query_engine(db_path=_CHROMA_DB_PATH)

    # Execute the LlamaIndex RAG pipeline
    response = query_engine.query(question)

    # Extract metadata for citations
    sources = [node.metadata for node in response.source_nodes]

    # Format a clean Markdown response for the AI Agent
    output = f"{str(response)}\n\n### Verified Sources:\n"
    for source in sources:
        file = source.get("file_name", "Unknown")
        header = source.get("header_path", "Unknown")
        output += f"- {file} ({header})\n"

    return output

if __name__ == "__main__":
    # 3. Run the server using Standard I/O (stdio) — the standard MCP transport
    mcp.run(transport="stdio")