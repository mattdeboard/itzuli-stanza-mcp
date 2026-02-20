from unittest.mock import Mock, patch

from core.workflow import process_translation_with_analysis, get_cached_stanza_pipeline
from core.types import AnalysisRow, TranslationResult


class TestAnalysisRow:
    def test_creates_analysis_row(self):
        row = AnalysisRow("kaixo", "(kaixo)", "interjection", "Animacy=Inan")

        assert row.word == "kaixo"
        assert row.lemma == "(kaixo)"
        assert row.upos == "interjection"
        assert row.feats == "Animacy=Inan"


class TestTranslationResult:
    def test_creates_translation_result(self):
        rows = [AnalysisRow("kaixo", "(kaixo)", "interjection", "Animacy=Inan")]
        result = TranslationResult(
            source_text="Kaixo!",
            source_language="eu",
            translated_text="Hello!",
            target_language="en",
            translation_id="trans-123",
            analysis_rows=rows,
        )

        assert result.source_text == "Kaixo!"
        assert result.source_language == "eu"
        assert result.translated_text == "Hello!"
        assert result.target_language == "en"
        assert result.translation_id == "trans-123"
        assert len(result.analysis_rows) == 1
        assert result.analysis_rows[0].word == "kaixo"


class TestProcessTranslationWithAnalysis:
    @patch("core.workflow.get_cached_stanza_pipeline")
    @patch("core.workflow.process_raw_analysis")
    @patch("core.workflow.Itzuli")
    def test_processes_eu_to_en_translation(self, mock_itzuli_class, mock_process_raw_analysis, mock_get_pipeline):
        mock_itzuli = Mock()
        mock_itzuli_class.return_value = mock_itzuli
        mock_itzuli.getTranslation.return_value = {"translated_text": "Hello!", "id": "trans-123"}

        mock_process_raw_analysis.return_value = [AnalysisRow("Kaixo", "kaixo", "INTJ", "Animacy=Inan")]

        result = process_translation_with_analysis(
            api_key="test-key", text="Kaixo!", source_language="eu", target_language="en"
        )

        assert result.source_text == "Kaixo!"
        assert result.source_language == "eu"
        assert result.translated_text == "Hello!"
        assert result.target_language == "en"
        assert result.translation_id == "trans-123"
        assert len(result.analysis_rows) == 1
        assert result.analysis_rows[0].word == "Kaixo"

        mock_itzuli.getTranslation.assert_called_once_with("Kaixo!", "eu", "en")
        mock_process_raw_analysis.assert_called_once_with(mock_get_pipeline.return_value, "Kaixo!")

    @patch("core.workflow.get_cached_stanza_pipeline")
    @patch("core.workflow.process_raw_analysis")
    @patch("core.workflow.Itzuli")
    def test_processes_en_to_eu_translation(self, mock_itzuli_class, mock_process_raw_analysis, mock_get_pipeline):
        mock_itzuli = Mock()
        mock_itzuli_class.return_value = mock_itzuli
        mock_itzuli.getTranslation.return_value = {"translated_text": "Kaixo!", "id": "trans-456"}

        mock_process_raw_analysis.return_value = [AnalysisRow("Kaixo", "kaixo", "INTJ", "Animacy=Inan")]

        result = process_translation_with_analysis(
            api_key="test-key", text="Hello!", source_language="en", target_language="eu"
        )

        assert result.source_text == "Hello!"
        assert result.source_language == "en"
        assert result.translated_text == "Kaixo!"
        assert result.target_language == "eu"
        assert result.translation_id == "trans-456"

        # Should analyze the translated (Basque) text, not the source English text
        mock_process_raw_analysis.assert_called_once_with(mock_get_pipeline.return_value, "Kaixo!")

    @patch("core.workflow.get_cached_stanza_pipeline")
    @patch("core.workflow.process_raw_analysis")
    @patch("core.workflow.Itzuli")
    def test_handles_empty_translation_id(self, mock_itzuli_class, mock_process_raw_analysis, mock_get_pipeline):
        mock_itzuli = Mock()
        mock_itzuli_class.return_value = mock_itzuli
        mock_itzuli.getTranslation.return_value = {
            "translated_text": "Hello!"
            # No "id" field
        }

        mock_process_raw_analysis.return_value = []

        result = process_translation_with_analysis(
            api_key="test-key", text="Kaixo!", source_language="eu", target_language="en"
        )

        assert result.translation_id == ""


class TestGetCachedStanzaPipeline:
    def test_caches_pipeline(self):
        # Clear any existing cached pipeline
        if hasattr(get_cached_stanza_pipeline, "_pipeline"):
            delattr(get_cached_stanza_pipeline, "_pipeline")

        with patch("core.workflow.create_pipeline") as mock_create:
            mock_pipeline = Mock()
            mock_create.return_value = mock_pipeline

            # First call should create pipeline
            pipeline1 = get_cached_stanza_pipeline()
            assert pipeline1 == mock_pipeline
            assert mock_create.call_count == 1

            # Second call should return cached pipeline
            pipeline2 = get_cached_stanza_pipeline()
            assert pipeline2 == mock_pipeline
            assert pipeline1 is pipeline2
            assert mock_create.call_count == 1  # Should not be called again
