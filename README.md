# ⚛️ React RAG Copilot

> A **production-grade, CPU-optimized** Retrieval-Augmented Generation (RAG) system that answers questions about React documentation with cited sources — exposed as both a **REST API** and an **MCP tool** for AI-powered IDEs.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-0.14-blueviolet?style=flat)](https://llamaindex.ai)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-1.5-orange?style=flat)](https://trychroma.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🧠 What Is This?

Most RAG tutorials stop at "it works on my machine." This project is built around the question: **what does a production-quality RAG pipeline actually look like?**

It features:
- **Two-stage retrieval** — vector search narrows to 15 candidates, a neural reranker picks the best 3
- **Zero GPU required** — every model (embeddings + reranker) runs on CPU
- **Two interfaces** — a FastAPI REST endpoint for apps, and an MCP server for AI assistants
- **Quantified quality** — evaluated with RAGAS (Faithfulness + Context Precision scores)

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔍 **Two-stage retrieval** | Vector search (top-15) → FlashRank neural reranker (top-3) |
| 🧩 **MCP Integration** | Works natively in Claude Desktop, Cursor, and any MCP client |
| 📚 **5 React hooks covered** | `useState`, `useEffect`, `useContext`, `useRef`, `useMemo` |
| ⚡ **Groq LLM** | Ultra-fast inference via Groq's free tier API |
| 🗄️ **Local vector DB** | ChromaDB with SQLite — no cloud infra needed |
| 📊 **RAGAS Evaluation** | Faithfulness & Context Precision metrics built-in |
| 🐍 **Modern FastAPI** | Uses the `lifespan` pattern (no deprecated `@on_event`) |
| 🔒 **Secure by default** | `.env` excluded from git, `.env.example` provided |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Ingestion (one-time)                        │
│                                                                     │
│   data/*.md  ──►  MarkdownNodeParser  ──►  all-MiniLM-L6-v2        │
│   (React docs)     (structure-aware       (local CPU embedding)     │
│                      chunking)                    │                 │
│                                                   ▼                 │
│                                          ChromaDB (local SQLite)    │
└─────────────────────────────────────────────────────────────────────┘
                                                   │
                                    ┌──────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Query Pipeline                              │
│                                                                     │
│   Question  ──►  Vector Search (top-15)  ──►  FlashRank Reranker   │
│                  (ChromaDB)                   (TinyBERT, top-3)     │
│                                                      │              │
│                                                      ▼              │
│                                               Groq LLM              │
│                                          (gpt-oss-20b)              │
│                                                      │              │
│                                                      ▼              │
│                              Answer + Source Citations              │
└─────────────────────────────────────────────────────────────────────┘
          │                              │
          ▼                              ▼
  REST API (/api/v1/ask)         MCP Tool (stdio)
  FastAPI + Uvicorn              Claude Desktop / Cursor
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **LLM** | [Groq](https://groq.com) (`gpt-oss-20b`) | Fastest inference on free tier |
| **Embeddings** | `all-MiniLM-L6-v2` (HuggingFace) | Tiny (80MB), runs on CPU |
| **Reranker** | FlashRank `ms-marco-TinyBERT-L-2-v2` | CPU neural reranker, massive precision boost |
| **Vector DB** | [ChromaDB](https://trychroma.com) (persistent) | Local, zero infrastructure |
| **RAG Framework** | [LlamaIndex](https://llamaindex.ai) v0.14 | Orchestration & document parsing |
| **API** | [FastAPI](https://fastapi.tiangolo.com) + Uvicorn | Async REST API |
| **MCP** | [FastMCP](https://github.com/jlowin/fastmcp) | MCP server via stdio |
| **Evaluation** | [RAGAS](https://ragas.io) | Quantified RAG quality metrics |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/rag-copilot.git
cd rag-copilot
```

### 2. Set up the environment

**Option A — Conda (recommended, fully pinned):**
```bash
conda env create -f environment.yml
conda activate rag_copilot
```

**Option B — pip:**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure your API key

```bash
cp .env.example .env
```

Then edit `.env` and add your [Groq API key](https://console.groq.com/keys) (free):

```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Ingest the React docs

This builds the local vector database. Run once after cloning:

```bash
python -c "from src.engine.indexer import build_index; build_index()"
```

### 5. Start the API server

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Visit **http://localhost:8000/docs** for the interactive Swagger UI.

---

## 🐳 Docker

The fastest way to run the project — no Python environment setup needed.

```bash
# 1. Add your API key
cp .env.example .env   # then edit .env with your GROQ_API_KEY

# 2. Build and start
docker compose up --build

# 3. Run the indexer once to populate the vector database
docker compose exec api python -c "from src.engine.indexer import build_index; build_index()"
```

The `chroma_db` is stored in a named Docker volume and persists across container restarts.

---

## 📡 API Usage

### `POST /api/v1/ask`

Ask any question about the indexed React hooks.

**curl:**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How does useState handle initial state functions?"}'
```

**Response:**
```json
{
  "answer": "When you pass a function as the initial state to useState, React treats it as an initializer function. It calls the function once during component initialization and uses its return value as the initial state. The function is never called again on re-renders.",
  "sources": [
    {
      "file_name": "react_useState.md",
      "header_path": "/Reference/useState(initialState)/Parameters/"
    },
    {
      "file_name": "react_useState.md",
      "header_path": "/Usage/Avoiding recreating the initial state/"
    }
  ]
}
```

**Python:**
```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/v1/ask",
    json={"question": "Can I call useEffect inside a loop?"}
)
print(response.json()["answer"])
```

---

## 🤖 MCP Integration (Claude Desktop / Cursor)

This project also runs as a **Model Context Protocol (MCP) server**, letting AI assistants like Claude or Cursor query the React docs directly during conversations.

### Claude Desktop

Edit your Claude Desktop config:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "react-rag-copilot": {
      "command": "C:\\Users\\YOUR_USER\\miniconda3\\envs\\rag_copilot\\python.exe",
      "args": ["D:\\Projects\\rag-copilot\\src\\mcp_server.py"]
    }
  }
}
```

### Cursor

In Cursor settings → MCP → Add server:
```json
{
  "react-rag-copilot": {
    "command": "python",
    "args": ["src/mcp_server.py"]
  }
}
```

Once connected, the AI has access to the `query_react_docs` tool and will cite sources from your local database automatically.

---

## 📊 Evaluation Results

The pipeline is evaluated using [RAGAS](https://ragas.io) on sample React hook questions:

| Question | Faithfulness | Context Precision |
|---|---|---|
| How does useState handle initial state functions? | **1.00** ✅ | **1.00** ✅ |
| Can you call useState inside a loop or condition? | **0.50** ⚠️ | **1.00** ✅ |

**Context Precision is near-perfect** — the two-stage reranker consistently surfaces the right document sections. **Faithfulness** dips on nuanced questions, an area for future prompt engineering work.

Run the evaluation yourself:
```bash
python -m src.evaluate
```

Results are saved to `rag_evaluation_results.csv`.

---

## 📁 Project Structure

```
rag-copilot/
├── data/                        # Knowledge base (Markdown docs)
│   ├── react_useState.md
│   ├── react_useEffect.md
│   ├── react_useContext.md
│   ├── react_useRef.md
│   └── react_useMemo.md
├── src/
│   ├── main.py                  # FastAPI app entrypoint
│   ├── mcp_server.py            # MCP server (stdio transport)
│   ├── evaluate.py              # RAGAS evaluation script
│   ├── api/
│   │   └── routes.py            # REST API routes + lifespan
│   └── engine/
│       ├── config.py            # LLM + embedding model setup
│       ├── indexer.py           # Document ingestion pipeline
│       └── retriever.py         # Query engine + reranker
├── chroma_db/                   # Local vector database (git-ignored)
├── .env.example                 # Environment variable template
├── environment.yml              # Conda environment spec
└── rag_evaluation_results.csv   # Latest RAGAS scores
```

---

## 🔑 Key Design Decisions

**Why two-stage retrieval?**
Simple top-k vector search optimizes for recall, not precision. Adding FlashRank's TinyBERT reranker — which scores full query-document pairs — consistently eliminates irrelevant chunks before they reach the LLM, reducing hallucinations.

**Why CPU-only?**
Making this GPU-dependent would exclude most developers. `all-MiniLM-L6-v2` is ~80MB and embeds at ~2000 sentences/second on a modern CPU. The TinyBERT reranker adds ~50ms of latency for a significant precision gain — a worthwhile tradeoff.

**Why MCP + REST API?**
Different consumers have different needs. The REST API is for application integrations and testing. The MCP server allows AI assistants to use the RAG pipeline as a grounding tool in real-time — a pattern that is becoming a standard in AI-native development.

---

## 📄 License

MIT © 2026

---

## 🙏 Acknowledgements

- [LlamaIndex](https://llamaindex.ai) for the RAG orchestration framework
- [Groq](https://groq.com) for blazing-fast LLM inference
- [ChromaDB](https://trychroma.com) for the local vector store
- [FlashRank](https://github.com/PrithivirajDamodaran/FlashRank) for the CPU-friendly reranker
- [RAGAS](https://ragas.io) for evaluation metrics
- [React](https://react.dev) for the documentation used as the knowledge base
