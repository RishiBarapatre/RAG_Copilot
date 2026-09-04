# =============================================================================
# test_api.py — Integration tests for the FastAPI /api/v1/ask endpoint
# =============================================================================
# Strategy: mock setup_globals() and get_query_engine() so the TestClient
# never touches real models or databases. Tests focus purely on HTTP
# contract: request validation, response shape, and error handling.
# =============================================================================

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


@pytest.fixture
def api_client(mock_query_engine):
    """
    A TestClient with the query engine mocked out.
    Patches both setup_globals (skips LLM/embedding init) and
    get_query_engine (returns a controllable mock engine).
    """
    with patch("src.api.routes.setup_globals"), \
         patch("src.api.routes.get_query_engine", return_value=mock_query_engine):
        from src.main import app
        with TestClient(app) as client:
            yield client


@pytest.fixture
def api_client_no_index():
    """
    A TestClient where the indexer has never been run.
    Simulates the real-world case where a user starts the server
    before running the ingestion step.
    
    Explicitly resets the module-level query_engine to None so this
    fixture is order-independent (a previous test may have set it).
    """
    import src.api.routes as routes_module
    original_engine = routes_module.query_engine
    routes_module.query_engine = None  # ensure clean state
    try:
        with patch("src.api.routes.setup_globals"), \
             patch("src.api.routes.get_query_engine", side_effect=Exception("Collection is empty")):
            from src.main import app
            with TestClient(app) as client:
                yield client
    finally:
        routes_module.query_engine = original_engine  # restore after test


class TestAskEndpoint:

    def test_returns_200_with_valid_question(self, api_client):
        """A well-formed request should return 200 with an answer and sources."""
        response = api_client.post(
            "/api/v1/ask",
            json={"question": "How does useState handle initial state functions?"}
        )
        assert response.status_code == 200
        body = response.json()
        assert "answer" in body
        assert "sources" in body
        assert isinstance(body["answer"], str)
        assert len(body["answer"]) > 0

    def test_response_sources_are_list_of_dicts(self, api_client):
        """Sources must be a list of dicts containing file metadata."""
        response = api_client.post(
            "/api/v1/ask",
            json={"question": "What is useEffect?"}
        )
        assert response.status_code == 200
        sources = response.json()["sources"]
        assert isinstance(sources, list)
        assert len(sources) > 0
        # Each source should be a dict with file metadata
        for source in sources:
            assert isinstance(source, dict)
            assert "file_name" in source

    def test_returns_422_when_question_field_missing(self, api_client):
        """Sending an empty body should return 422 Unprocessable Entity."""
        response = api_client.post("/api/v1/ask", json={})
        assert response.status_code == 422

    def test_returns_422_when_body_is_not_json(self, api_client):
        """Sending plain text instead of JSON should return 422."""
        response = api_client.post(
            "/api/v1/ask",
            content="this is not json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_returns_503_when_index_not_initialized(self, api_client_no_index):
        """
        If the indexer has never been run, the server should start but
        the /ask endpoint must return 503 (not 500 or a crash).
        """
        response = api_client_no_index.post(
            "/api/v1/ask",
            json={"question": "What is React?"}
        )
        assert response.status_code == 503
        assert "not initialized" in response.json()["detail"].lower()

    def test_query_engine_receives_exact_question(self, api_client, mock_query_engine):
        """The question from the request body must be passed verbatim to the engine."""
        question = "Can I call useState inside a loop?"
        api_client.post("/api/v1/ask", json={"question": question})
        mock_query_engine.query.assert_called_once_with(question)
