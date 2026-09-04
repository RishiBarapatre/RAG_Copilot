# =============================================================================
# test_config.py — Unit tests for src/engine/config.py
# =============================================================================

import os
import pytest
from unittest.mock import patch, MagicMock
from src.engine.config import setup_globals



class TestSetupGlobals:

    def test_raises_if_groq_api_key_missing(self, monkeypatch):
        """setup_globals() must raise ValueError when GROQ_API_KEY is absent.

        We also patch load_dotenv to a no-op — without this, load_dotenv()
        reads the real .env file from disk and restores the key, defeating
        the monkeypatch.
        """
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        with patch("src.engine.config.load_dotenv"):  # block .env from restoring the key
            with pytest.raises(ValueError, match="GROQ_API_KEY"):
                setup_globals()

    def test_raises_if_groq_api_key_empty_string(self, monkeypatch):
        """An empty GROQ_API_KEY should also fail — it's not a valid key."""
        monkeypatch.setenv("GROQ_API_KEY", "")
        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            setup_globals()

    def test_configures_groq_llm_with_correct_model(self, monkeypatch):
        """setup_globals() should set Settings.llm to a Groq instance with the right model."""
        monkeypatch.setenv("GROQ_API_KEY", "test-key-abc123")

        with patch("src.engine.config.Groq") as mock_groq_cls, \
             patch("src.engine.config.HuggingFaceEmbedding"), \
             patch("src.engine.config.Settings"):
            setup_globals()
            mock_groq_cls.assert_called_once_with(
                model="openai/gpt-oss-20b",
                api_key="test-key-abc123"
            )

    def test_configures_minilm_embedding_model(self, monkeypatch):
        """setup_globals() should set Settings.embed_model to all-MiniLM-L6-v2."""
        monkeypatch.setenv("GROQ_API_KEY", "test-key-abc123")

        with patch("src.engine.config.Groq"), \
             patch("src.engine.config.HuggingFaceEmbedding") as mock_embed_cls, \
             patch("src.engine.config.Settings"):
            setup_globals()
            mock_embed_cls.assert_called_once_with(model_name="all-MiniLM-L6-v2")

    def test_accepts_custom_dotenv_path(self, monkeypatch, tmp_path):
        """setup_globals() should load a .env from a custom path when provided."""
        env_file = tmp_path / ".env"
        env_file.write_text("GROQ_API_KEY=custom-path-key\n")

        with patch("src.engine.config.Groq"), \
             patch("src.engine.config.HuggingFaceEmbedding"), \
             patch("src.engine.config.Settings"):
            # Should not raise — key comes from the custom file
            setup_globals(dotenv_path=str(env_file))
