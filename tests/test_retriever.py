# =============================================================================
# test_retriever.py — Unit tests for src/engine/retriever.py
# =============================================================================
# ChromaDB and LlamaIndex are both mocked so these tests run instantly
# without any disk I/O, network calls, or model loading.
# =============================================================================

import pytest
from unittest.mock import patch, MagicMock


class TestGetQueryEngine:

    def test_returns_a_query_engine(self):
        """get_query_engine() should return a LlamaIndex query engine object."""
        mock_collection = MagicMock()
        mock_db = MagicMock()
        mock_db.get_or_create_collection.return_value = mock_collection

        mock_index = MagicMock()
        mock_engine = MagicMock()
        mock_index.as_query_engine.return_value = mock_engine

        with patch("src.engine.retriever.chromadb.PersistentClient", return_value=mock_db), \
             patch("src.engine.retriever.ChromaVectorStore"), \
             patch("src.engine.retriever.VectorStoreIndex") as mock_index_cls, \
             patch("src.engine.retriever.FlashRankRerank"):
            mock_index_cls.from_vector_store.return_value = mock_index

            from src.engine.retriever import get_query_engine
            engine = get_query_engine(db_path="./fake_db")

            assert engine is mock_engine

    def test_connects_to_correct_chroma_collection(self):
        """The retriever must always connect to the 'tech_docs' collection."""
        mock_db = MagicMock()

        with patch("src.engine.retriever.chromadb.PersistentClient", return_value=mock_db), \
             patch("src.engine.retriever.ChromaVectorStore"), \
             patch("src.engine.retriever.VectorStoreIndex") as mock_index_cls, \
             patch("src.engine.retriever.FlashRankRerank"):
            mock_index_cls.from_vector_store.return_value = MagicMock()

            from src.engine.retriever import get_query_engine
            get_query_engine(db_path="./test_db")

            mock_db.get_or_create_collection.assert_called_once_with("tech_docs")

    def test_reranker_uses_correct_model_and_top_n(self):
        """The reranker must use TinyBERT with top_n=3 for CPU efficiency."""
        mock_db = MagicMock()

        with patch("src.engine.retriever.chromadb.PersistentClient", return_value=mock_db), \
             patch("src.engine.retriever.ChromaVectorStore"), \
             patch("src.engine.retriever.VectorStoreIndex") as mock_index_cls, \
             patch("src.engine.retriever.FlashRankRerank") as mock_reranker_cls:
            mock_index_cls.from_vector_store.return_value = MagicMock()

            from src.engine.retriever import get_query_engine
            get_query_engine()

            mock_reranker_cls.assert_called_once_with(
                top_n=3,
                model="ms-marco-TinyBERT-L-2-v2"
            )

    def test_vector_search_uses_top_15_candidates(self):
        """Vector search must fetch 15 candidates before reranking to ensure recall."""
        mock_db = MagicMock()
        mock_index = MagicMock()

        with patch("src.engine.retriever.chromadb.PersistentClient", return_value=mock_db), \
             patch("src.engine.retriever.ChromaVectorStore"), \
             patch("src.engine.retriever.VectorStoreIndex") as mock_index_cls, \
             patch("src.engine.retriever.FlashRankRerank"):
            mock_index_cls.from_vector_store.return_value = mock_index

            from src.engine.retriever import get_query_engine
            get_query_engine()

            # Verify as_query_engine was called with similarity_top_k=15
            call_kwargs = mock_index.as_query_engine.call_args.kwargs
            assert call_kwargs.get("similarity_top_k") == 15
