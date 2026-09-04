# =============================================================================
# conftest.py — Shared pytest fixtures
# =============================================================================

import pytest
from unittest.mock import MagicMock


def _make_mock_node(file_name: str = "react_useState.md", header: str = "/Reference/") -> MagicMock:
    """Build a fake LlamaIndex source node with metadata."""
    node = MagicMock()
    node.metadata = {"file_name": file_name, "header_path": header}
    return node


def _make_mock_response(text: str = "This is a test answer about React hooks.") -> MagicMock:
    """Build a fake LlamaIndex response object."""
    response = MagicMock()
    response.__str__ = lambda self: text
    response.source_nodes = [
        _make_mock_node("react_useState.md", "/Reference/useState/"),
        _make_mock_node("react_useEffect.md", "/Reference/useEffect/"),
    ]
    return response


@pytest.fixture
def mock_llama_response():
    """A canned LlamaIndex response — reusable across tests."""
    return _make_mock_response()


@pytest.fixture
def mock_query_engine(mock_llama_response):
    """A mock query engine that returns a predictable response."""
    engine = MagicMock()
    engine.query.return_value = mock_llama_response
    return engine
