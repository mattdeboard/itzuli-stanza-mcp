"""Core Itzuli+Stanza pipeline for translation with morphological analysis."""

from dataclasses import dataclass
from typing import List
import logging

from Itzuli import Itzuli
from itzuli_stanza_mcp.nlp import create_pipeline, process_input, LanguageCode

logger = logging.getLogger("itzuli-stanza-pipeline")


@dataclass
class AnalysisRow:
    """Represents a single word analysis row."""

    word: str
    lemma: str
    upos: str
    feats: str


@dataclass
class TranslationResult:
    """Result of translation with morphological analysis."""

    source_text: str
    source_language: LanguageCode
    translated_text: str
    target_language: LanguageCode
    translation_id: str
    analysis_rows: List[AnalysisRow]


def get_cached_stanza_pipeline():
    """Get or create Stanza pipeline (cached)."""
    if not hasattr(get_cached_stanza_pipeline, "_pipeline"):
        get_cached_stanza_pipeline._pipeline = create_pipeline()
    return get_cached_stanza_pipeline._pipeline


def process_translation_with_analysis(
    api_key: str,
    text: str,
    source_language: LanguageCode,
    target_language: LanguageCode,
    output_language: LanguageCode = "en",
) -> TranslationResult:
    """
    Translate text and provide morphological analysis of Basque text.

    Args:
        api_key: Itzuli API key
        text: Text to translate
        source_language: Source language code
        target_language: Target language code
        output_language: Language for morphological analysis labels

    Returns:
        TranslationResult with translation and analysis data
    """
    # Get translation from Itzuli
    itzuli_client = Itzuli(api_key)
    translation_data = itzuli_client.getTranslation(text, source_language, target_language)
    translated_text = translation_data.get("translated_text", "")
    translation_id = translation_data.get("id", "")

    # Determine which text to analyze (always analyze Basque text)
    basque_text = text if source_language == "eu" else translated_text

    # Perform morphological analysis
    stanza_pipeline = get_cached_stanza_pipeline()
    analysis_tuples = process_input(stanza_pipeline, basque_text, output_language)
    analysis_rows = [
        AnalysisRow(word=word, lemma=lemma, upos=upos, feats=feats) for word, lemma, upos, feats in analysis_tuples
    ]

    return TranslationResult(
        source_text=text,
        source_language=source_language,
        translated_text=translated_text,
        target_language=target_language,
        translation_id=translation_id,
        analysis_rows=analysis_rows,
    )
