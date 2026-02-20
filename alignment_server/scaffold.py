"""Scaffold generator for alignment data from dual analysis output."""

from pathlib import Path
from typing import List

from core.types import AnalysisRow
from alignment_server.types import (
    Token,
    TokenizedSentence,
    AlignmentLayers,
    SentencePair,
    AlignmentData,
)
from core.i18n import FRIENDLY_FEATS


def parse_features_string(feats_string: str, language: str = "en") -> List[str]:
    """
    Parse Universal Dependencies features string into friendly descriptive list.

    Args:
        feats_string: Pipe-delimited "Key=Value|Key=Value" string from Stanza
        language: Language for feature descriptions (defaults to English)

    Returns:
        List of lowercase descriptive strings
    """
    if not feats_string:
        return []

    friendly_feats = FRIENDLY_FEATS.get(language, FRIENDLY_FEATS["en"])
    features = []

    for feat in feats_string.split("|"):
        feat = feat.strip()
        if "=" in feat:
            # Try to find friendly mapping
            friendly = friendly_feats.get(feat, feat.split("=")[1].lower())
            features.append(friendly)
        else:
            # Handle cases where there's no = (shouldn't happen in UD but just in case)
            features.append(feat.lower())

    return features


def build_scaffold(
    source_rows: List[AnalysisRow],
    target_rows: List[AnalysisRow],
    source_lang: str,
    target_lang: str,
    source_text: str,
    target_text: str,
    sentence_id: str,
) -> SentencePair:
    """
    Build alignment scaffold from dual analysis output.

    Args:
        source_rows: Analysis rows for source text
        target_rows: Analysis rows for target text
        source_lang: Source language code
        target_lang: Target language code
        source_text: Original source text
        target_text: Translated text
        sentence_id: Unique ID for this sentence pair

    Returns:
        SentencePair with populated tokens but empty alignment layers
    """
    # Build source tokens
    source_tokens = []
    for i, row in enumerate(source_rows):
        token = Token(
            id=f"s{i}",
            form=row.word,
            lemma=row.lemma,
            pos=row.upos.lower(),
            features=parse_features_string(row.feats, "en"),  # Always use English for consistency
        )
        source_tokens.append(token)

    # Build target tokens
    target_tokens = []
    for i, row in enumerate(target_rows):
        token = Token(
            id=f"t{i}",
            form=row.word,
            lemma=row.lemma,
            pos=row.upos.lower(),
            features=parse_features_string(row.feats, "en"),  # Always use English for consistency
        )
        target_tokens.append(token)

    # Build tokenized sentences
    source_sentence = TokenizedSentence(
        lang=source_lang,
        text=source_text,
        tokens=source_tokens,
    )

    target_sentence = TokenizedSentence(
        lang=target_lang,
        text=target_text,
        tokens=target_tokens,
    )

    # Create empty alignment layers
    empty_layers = AlignmentLayers()

    # Build sentence pair
    sentence_pair = SentencePair(
        id=sentence_id,
        source=source_sentence,
        target=target_sentence,
        layers=empty_layers,
    )

    return sentence_pair


def save_alignment_data(alignment_data: AlignmentData, file_path: str) -> None:
    """
    Save AlignmentData as pretty-printed JSON file.

    Args:
        alignment_data: AlignmentData object to save
        file_path: Path to save JSON file
    """
    json_str = alignment_data.model_dump_json(indent=2, exclude_unset=False)
    Path(file_path).write_text(json_str, encoding="utf-8")


def load_alignment_data(file_path: str) -> AlignmentData:
    """
    Load AlignmentData from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        AlignmentData object
    """
    json_content = Path(file_path).read_text(encoding="utf-8")
    return AlignmentData.model_validate_json(json_content)


def create_scaffold_from_dual_analysis(
    source_analysis: List[AnalysisRow],
    target_analysis: List[AnalysisRow],
    source_lang: str,
    target_lang: str,
    source_text: str,
    target_text: str,
    sentence_id: str,
) -> AlignmentData:
    """
    Convenience function to create complete AlignmentData scaffold from dual analysis.

    Args:
        source_analysis: Analysis of source text
        target_analysis: Analysis of target text
        source_lang: Source language code
        target_lang: Target language code
        source_text: Original source text
        target_text: Translated text
        sentence_id: Unique ID for this sentence pair

    Returns:
        AlignmentData with single SentencePair (empty alignment layers)
    """
    sentence_pair = build_scaffold(
        source_analysis,
        target_analysis,
        source_lang,
        target_lang,
        source_text,
        target_text,
        sentence_id,
    )

    return AlignmentData(sentences=[sentence_pair])
