"""Common types for the Itzuli+Stanza pipeline."""

from dataclasses import dataclass
from typing import List, Literal

LanguageCode = Literal["eu", "en", "es", "fr"]


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
