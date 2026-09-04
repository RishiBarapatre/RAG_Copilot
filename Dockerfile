# =============================================================================
# React RAG Copilot — Dockerfile
# =============================================================================
# Multi-stage build:
#   Stage 1 (builder): install all Python dependencies into a venv
#   Stage 2 (runtime): copy only the venv + source — no build tools in prod
# =============================================================================

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies first (layer-cached if requirements.txt unchanged)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy the built venv from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source code and knowledge base
COPY src/ ./src/
COPY data/ ./data/

# The vector database is stored in a volume (see docker-compose.yml)
# The .env file is injected at runtime — never baked into the image
VOLUME ["/app/chroma_db"]

# Expose the FastAPI port
EXPOSE 8000

# Healthcheck — ensures the container is considered healthy only when the
# API is actually responding (after the lifespan startup finishes)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# Run the server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
