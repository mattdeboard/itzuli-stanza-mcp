from unittest.mock import Mock

from itzuli_nlp.core.nlp import process_raw_analysis, create_pipeline
from itzuli_nlp.core.types import AnalysisRow


class TestProcessRawAnalysis:
    def test_returns_analysis_row_objects(self):
        # Mock pipeline and doc structure
        mock_pipeline = Mock()
        mock_doc = Mock()
        mock_sentence = Mock()
        mock_word = Mock()

        # Set up mock word with Stanza data
        mock_word.text = "Kaixo"
        mock_word.lemma = "kaixo"
        mock_word.upos = "INTJ"
        mock_word.feats = "Animacy=Inan"

        # Wire up the mock structure
        mock_sentence.words = [mock_word]
        mock_doc.sentences = [mock_sentence]
        mock_pipeline.return_value = mock_doc

        result = process_raw_analysis(mock_pipeline, "Kaixo!")

        assert len(result) == 1
        assert isinstance(result[0], AnalysisRow)
        assert result[0].word == "Kaixo"
        assert result[0].lemma == "kaixo"
        assert result[0].upos == "INTJ"
        assert result[0].feats == "Animacy=Inan"

        mock_pipeline.assert_called_once_with("Kaixo!")

    def test_handles_empty_features(self):
        # Mock with no features
        mock_pipeline = Mock()
        mock_doc = Mock()
        mock_sentence = Mock()
        mock_word = Mock()

        mock_word.text = "test"
        mock_word.lemma = "test"
        mock_word.upos = "NOUN"
        mock_word.feats = None

        mock_sentence.words = [mock_word]
        mock_doc.sentences = [mock_sentence]
        mock_pipeline.return_value = mock_doc

        result = process_raw_analysis(mock_pipeline, "test")

        assert len(result) == 1
        assert result[0].feats == ""

    def test_handles_multiple_sentences(self):
        # Mock with multiple sentences
        mock_pipeline = Mock()
        mock_doc = Mock()

        # First sentence
        mock_sentence1 = Mock()
        mock_word1 = Mock()
        mock_word1.text = "Kaixo"
        mock_word1.lemma = "kaixo"
        mock_word1.upos = "INTJ"
        mock_word1.feats = "Animacy=Inan"
        mock_sentence1.words = [mock_word1]

        # Second sentence
        mock_sentence2 = Mock()
        mock_word2 = Mock()
        mock_word2.text = "mundua"
        mock_word2.lemma = "mundu"
        mock_word2.upos = "NOUN"
        mock_word2.feats = "Case=Abs|Definite=Def|Number=Sing"
        mock_sentence2.words = [mock_word2]

        mock_doc.sentences = [mock_sentence1, mock_sentence2]
        mock_pipeline.return_value = mock_doc

        result = process_raw_analysis(mock_pipeline, "Kaixo mundua!")

        assert len(result) == 2
        assert result[0].word == "Kaixo"
        assert result[1].word == "mundua"


class TestCreatePipeline:
    def test_creates_basque_pipeline(self):
        # This is more of an integration test - we can't easily mock Stanza
        # Just ensure it returns a pipeline object without errors
        pipeline = create_pipeline()

        # Basic validation that it's a Stanza pipeline
        assert hasattr(pipeline, "__call__")  # Should be callable
        assert hasattr(pipeline, "processors")  # Should have processors attribute
