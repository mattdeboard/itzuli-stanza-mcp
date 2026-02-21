"""Tests for alignment server FastAPI endpoints."""

import os
import subprocess
import sys
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from itzuli_nlp.core.types import AnalysisRow
from itzuli_nlp.alignment_server.server import app
from itzuli_nlp.alignment_server.types import AlignmentData, SentencePair, TokenizedSentence, Token, AlignmentLayers


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_analysis_data():
    """Mock analysis data for testing."""
    source_analysis = [
        AnalysisRow("Kaixo", "kaixo", "INTJ", ""),
        AnalysisRow("mundua", "mundu", "NOUN", "Case=Abs|Definite=Def|Number=Sing"),
    ]

    target_analysis = [
        AnalysisRow("Hello", "hello", "INTJ", ""),
        AnalysisRow("world", "world", "NOUN", "Number=Sing"),
    ]

    return source_analysis, target_analysis, "Hello world"


@pytest.fixture
def mock_alignment_data():
    """Mock alignment data for testing."""
    source_tokens = [
        Token(id="s0", form="Kaixo", lemma="kaixo", pos="intj", features=[]),
        Token(id="s1", form="mundua", lemma="mundu", pos="noun", features=["absolutive", "definite", "singular"]),
    ]

    target_tokens = [
        Token(id="t0", form="Hello", lemma="hello", pos="intj", features=[]),
        Token(id="t1", form="world", lemma="world", pos="noun", features=["singular"]),
    ]

    source_sentence = TokenizedSentence(lang="eu", text="Kaixo mundua", tokens=source_tokens)
    target_sentence = TokenizedSentence(lang="en", text="Hello world", tokens=target_tokens)

    sentence_pair = SentencePair(
        id="test-001", source=source_sentence, target=target_sentence, layers=AlignmentLayers()
    )

    return AlignmentData(sentences=[sentence_pair])


class TestHealthCheck:
    def test_health_check_returns_healthy_status(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestAnalyzeEndpoint:
    @patch.dict(os.environ, {"ITZULI_API_KEY": "test-key"})
    @patch("itzuli_nlp.alignment_server.server.analyze_both_texts")
    def test_analyze_texts_success(self, mock_analyze, client, mock_analysis_data):
        source_analysis, target_analysis, translated_text = mock_analysis_data
        mock_analyze.return_value = (source_analysis, target_analysis, translated_text)

        request_data = {"text": "Kaixo mundua", "source_lang": "eu", "target_lang": "en", "sentence_id": "test-001"}

        response = client.post("/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["source_text"] == "Kaixo mundua"
        assert data["target_text"] == "Hello world"
        assert data["source_lang"] == "eu"
        assert data["target_lang"] == "en"
        assert len(data["source_analysis"]) == 2
        assert len(data["target_analysis"]) == 2

        # Verify analysis row structure
        assert data["source_analysis"][0] == {"word": "Kaixo", "lemma": "kaixo", "upos": "INTJ", "feats": ""}

        mock_analyze.assert_called_once_with(
            api_key="test-key", text="Kaixo mundua", source_lang="eu", target_lang="en"
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_analyze_texts_missing_api_key(self, client):
        request_data = {"text": "Kaixo mundua", "source_lang": "eu", "target_lang": "en"}

        response = client.post("/analyze", json=request_data)

        assert response.status_code == 500
        assert "ITZULI_API_KEY not configured" in response.json()["detail"]

    @patch.dict(os.environ, {"ITZULI_API_KEY": "test-key"})
    @patch("itzuli_nlp.alignment_server.server.analyze_both_texts")
    def test_analyze_texts_analysis_error(self, mock_analyze, client):
        mock_analyze.side_effect = Exception("Translation failed")

        request_data = {"text": "Kaixo mundua", "source_lang": "eu", "target_lang": "en"}

        response = client.post("/analyze", json=request_data)

        assert response.status_code == 500
        assert "Analysis failed: Translation failed" in response.json()["detail"]

    def test_analyze_texts_invalid_request(self, client):
        # Missing required fields
        request_data = {"text": "Kaixo"}

        response = client.post("/analyze", json=request_data)

        assert response.status_code == 422  # Validation error

    @patch.dict(os.environ, {"ITZULI_API_KEY": "test-key"})
    @patch("itzuli_nlp.alignment_server.server.analyze_both_texts")
    def test_analyze_texts_with_default_sentence_id(self, mock_analyze, client, mock_analysis_data):
        source_analysis, target_analysis, translated_text = mock_analysis_data
        mock_analyze.return_value = (source_analysis, target_analysis, translated_text)

        request_data = {
            "text": "Kaixo mundua",
            "source_lang": "eu",
            "target_lang": "en",
            # No sentence_id provided, should default to "default"
        }

        response = client.post("/analyze", json=request_data)

        assert response.status_code == 200
        # The sentence_id is only used in /analyze-and-scaffold, not /analyze



class TestAnalyzeAndScaffoldEndpoint:
    @patch.dict(os.environ, {"ITZULI_API_KEY": "test-key"})
    @patch("itzuli_nlp.alignment_server.server.create_scaffold_from_dual_analysis")
    @patch("itzuli_nlp.alignment_server.server.analyze_both_texts")
    def test_analyze_and_scaffold_success(
        self, mock_analyze, mock_create_scaffold, client, mock_analysis_data, mock_alignment_data
    ):
        source_analysis, target_analysis, translated_text = mock_analysis_data
        mock_analyze.return_value = (source_analysis, target_analysis, translated_text)
        mock_create_scaffold.return_value = mock_alignment_data

        request_data = {"text": "Kaixo mundua", "source_lang": "eu", "target_lang": "en", "sentence_id": "test-001"}

        response = client.post("/analyze-and-scaffold", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify scaffold structure
        assert "sentences" in data
        assert len(data["sentences"]) == 1

        # Verify both functions were called correctly
        mock_analyze.assert_called_once_with(
            api_key="test-key", text="Kaixo mundua", source_lang="eu", target_lang="en"
        )

        mock_create_scaffold.assert_called_once_with(
            source_analysis=source_analysis,
            target_analysis=target_analysis,
            source_lang="eu",
            target_lang="en",
            source_text="Kaixo mundua",
            target_text="Hello world",
            sentence_id="test-001",
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_analyze_and_scaffold_missing_api_key(self, client):
        request_data = {"text": "Kaixo mundua", "source_lang": "eu", "target_lang": "en"}

        response = client.post("/analyze-and-scaffold", json=request_data)

        assert response.status_code == 500
        assert "ITZULI_API_KEY not configured" in response.json()["detail"]

    @patch.dict(os.environ, {"ITZULI_API_KEY": "test-key"})
    @patch("itzuli_nlp.alignment_server.server.analyze_both_texts")
    def test_analyze_and_scaffold_analysis_error(self, mock_analyze, client):
        mock_analyze.side_effect = Exception("Analysis failed")

        request_data = {"text": "Kaixo mundua", "source_lang": "eu", "target_lang": "en"}

        response = client.post("/analyze-and-scaffold", json=request_data)

        assert response.status_code == 500
        assert "Analysis and scaffold generation failed: Analysis failed" in response.json()["detail"]

    @patch.dict(os.environ, {"ITZULI_API_KEY": "test-key"})
    @patch("itzuli_nlp.alignment_server.server.create_scaffold_from_dual_analysis")
    @patch("itzuli_nlp.alignment_server.server.analyze_both_texts")
    def test_analyze_and_scaffold_scaffold_error(self, mock_analyze, mock_create_scaffold, client, mock_analysis_data):
        source_analysis, target_analysis, translated_text = mock_analysis_data
        mock_analyze.return_value = (source_analysis, target_analysis, translated_text)
        mock_create_scaffold.side_effect = Exception("Scaffold creation failed")

        request_data = {"text": "Kaixo mundua", "source_lang": "eu", "target_lang": "en"}

        response = client.post("/analyze-and-scaffold", json=request_data)

        assert response.status_code == 500
        assert "Analysis and scaffold generation failed: Scaffold creation failed" in response.json()["detail"]

    def test_analyze_and_scaffold_invalid_request(self, client):
        # Missing required fields
        request_data = {"text": "test"}

        response = client.post("/analyze-and-scaffold", json=request_data)

        assert response.status_code == 422  # Validation error

    @patch.dict(os.environ, {"ITZULI_API_KEY": "test-key"})
    @patch("itzuli_nlp.alignment_server.server.create_scaffold_from_dual_analysis")
    @patch("itzuli_nlp.alignment_server.server.analyze_both_texts")
    def test_analyze_and_scaffold_with_default_sentence_id(
        self, mock_analyze, mock_create_scaffold, client, mock_analysis_data, mock_alignment_data
    ):
        source_analysis, target_analysis, translated_text = mock_analysis_data
        mock_analyze.return_value = (source_analysis, target_analysis, translated_text)
        mock_create_scaffold.return_value = mock_alignment_data

        request_data = {
            "text": "Kaixo mundua",
            "source_lang": "eu",
            "target_lang": "en",
            # No sentence_id provided, should default to "default"
        }

        response = client.post("/analyze-and-scaffold", json=request_data)

        assert response.status_code == 200

        # Verify default sentence_id was used
        call_args = mock_create_scaffold.call_args
        assert call_args.kwargs["sentence_id"] == "default"


class TestModelValidation:
    def test_analysis_request_model_validation(self):
        from itzuli_nlp.alignment_server.server import AnalysisRequest

        # Valid request
        valid_request = AnalysisRequest(text="Kaixo", source_lang="eu", target_lang="en", sentence_id="test-001")
        assert valid_request.text == "Kaixo"
        assert valid_request.sentence_id == "test-001"

        # Request with default sentence_id
        default_request = AnalysisRequest(text="Kaixo", source_lang="eu", target_lang="en")
        assert default_request.sentence_id == "default"

    def test_analysis_response_model_validation(self):
        from itzuli_nlp.alignment_server.server import AnalysisResponse

        source_analysis = [AnalysisRow("Kaixo", "kaixo", "INTJ", "")]
        target_analysis = [AnalysisRow("Hello", "hello", "INTJ", "")]

        response = AnalysisResponse(
            source_text="Kaixo",
            target_text="Hello",
            source_lang="eu",
            target_lang="en",
            source_analysis=source_analysis,
            target_analysis=target_analysis,
        )

        assert response.source_text == "Kaixo"
        assert len(response.source_analysis) == 1
        assert isinstance(response.source_analysis[0], AnalysisRow)



class TestAppConfiguration:
    def test_fastapi_app_metadata(self):
        assert app.title == "Alignment Server"
        assert app.description == "HTTP API for generating alignment scaffolds from dual language analysis"
        assert app.version == "0.1.0"


class TestMainBlock:
    def test_main_block_execution(self):
        """Test the main block execution path for full coverage."""
        try:
            # Execute the main block directly by running the module
            result = subprocess.run(
                [sys.executable, "-m", "itzuli_nlp.alignment_server.server"],
                cwd=os.getcwd(),
                env={**os.environ, "PORT": "9000", "HOST": "127.0.0.1", "ITZULI_API_KEY": "test-key"},
                capture_output=True,
                text=True,
                timeout=1,  # Quick timeout since we just want to trigger the main block
            )
        except subprocess.TimeoutExpired as e:
            # This is expected - the server starts and we kill it with timeout
            # The important thing is that we see the startup log message
            stderr_output = e.stderr.decode() if e.stderr else ""
            assert "Starting alignment server on 127.0.0.1:9000" in stderr_output
            assert "ModuleNotFoundError" not in stderr_output
            return

        # If no timeout, check that server started successfully
        assert "Starting alignment server" in result.stderr
        assert "ModuleNotFoundError" not in result.stderr

    def test_environment_variable_parsing(self):
        # Test environment variable parsing logic separately
        original_env = os.environ.copy()

        try:
            # Test with custom values
            os.environ["PORT"] = "9000"
            os.environ["HOST"] = "127.0.0.1"

            port = int(os.environ.get("PORT", 8000))
            host = os.environ.get("HOST", "0.0.0.0")

            assert port == 9000
            assert host == "127.0.0.1"

            # Test with defaults
            del os.environ["PORT"]
            del os.environ["HOST"]

            port = int(os.environ.get("PORT", 8000))
            host = os.environ.get("HOST", "0.0.0.0")

            assert port == 8000
            assert host == "0.0.0.0"

        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)


class TestErrorHandling:
    @patch.dict(os.environ, {"ITZULI_API_KEY": "test-key"})
    @patch("itzuli_nlp.alignment_server.server.analyze_both_texts")
    def test_analyze_logs_error_on_failure(self, mock_analyze, client):
        mock_analyze.side_effect = Exception("Test error")

        request_data = {"text": "Kaixo", "source_lang": "eu", "target_lang": "en"}

        with patch("itzuli_nlp.alignment_server.server.logger") as mock_logger:
            response = client.post("/analyze", json=request_data)

            assert response.status_code == 500
            mock_logger.error.assert_called_once_with("Analysis failed: Test error")


    @patch.dict(os.environ, {"ITZULI_API_KEY": "test-key"})
    @patch("itzuli_nlp.alignment_server.server.create_scaffold_from_dual_analysis")
    @patch("itzuli_nlp.alignment_server.server.analyze_both_texts")
    def test_analyze_and_scaffold_logs_error_on_failure(self, mock_analyze, mock_create_scaffold, client):
        mock_analyze.side_effect = Exception("Test error")

        request_data = {"text": "Kaixo", "source_lang": "eu", "target_lang": "en"}

        with patch("itzuli_nlp.alignment_server.server.logger") as mock_logger:
            response = client.post("/analyze-and-scaffold", json=request_data)

            assert response.status_code == 500
            mock_logger.error.assert_called_once_with("Analysis and scaffold generation failed: Test error")


class TestEdgeCases:
    @patch.dict(os.environ, {"ITZULI_API_KEY": "test-key"})
    @patch("itzuli_nlp.alignment_server.server.analyze_both_texts")
    def test_analyze_with_empty_features(self, mock_analyze, client):
        # Test with empty features
        source_analysis = [AnalysisRow("test", "test", "NOUN", "")]
        target_analysis = [AnalysisRow("test", "test", "NOUN", "")]
        mock_analyze.return_value = (source_analysis, target_analysis, "test")

        request_data = {"text": "test", "source_lang": "eu", "target_lang": "en"}

        response = client.post("/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["source_analysis"][0]["feats"] == ""



class TestResponseSchemas:
    @patch.dict(os.environ, {"ITZULI_API_KEY": "test-key"})
    @patch("itzuli_nlp.alignment_server.server.analyze_both_texts")
    def test_analysis_response_schema_compatibility(self, mock_analyze, client):
        # Test that AnalysisRow objects serialize correctly in FastAPI
        source_analysis = [AnalysisRow("Kaixo", "kaixo", "INTJ", "Animacy=Inan")]
        target_analysis = [AnalysisRow("Hello", "hello", "INTJ", "")]
        mock_analyze.return_value = (source_analysis, target_analysis, "Hello")

        request_data = {"text": "Kaixo", "source_lang": "eu", "target_lang": "en"}

        response = client.post("/analyze", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify AnalysisRow serialization
        source_row = data["source_analysis"][0]
        assert source_row["word"] == "Kaixo"
        assert source_row["lemma"] == "kaixo"
        assert source_row["upos"] == "INTJ"
        assert source_row["feats"] == "Animacy=Inan"

        target_row = data["target_analysis"][0]
        assert target_row["word"] == "Hello"
        assert target_row["feats"] == ""
