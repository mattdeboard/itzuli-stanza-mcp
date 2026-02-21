"""Formatters for Itzuli+Stanza pipeline output."""

import json
from typing import List, Tuple
from .types import TranslationResult, LanguageCode
from .i18n import LANGUAGE_NAMES, OUTPUT_LABELS, FRIENDLY_FEATS, FRIENDLY_UPOS, QUIRKS


def apply_friendly_mappings(
    raw_analysis: List[Tuple[str, str, str, str]], language: LanguageCode = "en"
) -> List[Tuple[str, str, str, str]]:
    """Convert raw Stanza analysis to human-friendly format."""
    friendly_feats = FRIENDLY_FEATS.get(language, FRIENDLY_FEATS["en"])
    friendly_upos = FRIENDLY_UPOS.get(language, FRIENDLY_UPOS["en"])
    quirks = QUIRKS.get(language, QUIRKS["en"])

    friendly_rows = []

    for word, lemma, upos, feats in raw_analysis:
        # Apply friendly mappings
        descs = []
        quirk = quirks.get(word.lower())
        if quirk:
            descs.append(quirk)
        elif feats:
            for feat in feats.split("|"):
                friendly = friendly_feats.get(feat, feat)
                if friendly:
                    descs.append(friendly)

        upos_friendly = friendly_upos.get(upos, upos)
        friendly_rows.append((word, f"({lemma})", upos_friendly, ", ".join(descs)))

    return friendly_rows


def format_as_markdown_table(result: TranslationResult, output_language: LanguageCode = "en") -> str:
    """Format TranslationResult as markdown table with 100-column limit."""
    # Get localized labels and language names
    labels = OUTPUT_LABELS.get(output_language, OUTPUT_LABELS["en"])
    language_names = LANGUAGE_NAMES.get(output_language, LANGUAGE_NAMES["en"])

    # Convert raw analysis to friendly format
    raw_rows = [(row.word, row.lemma, row.upos, row.feats) for row in result.analysis_rows]
    friendly_rows = apply_friendly_mappings(raw_rows, output_language)

    # Format output with 100-column limit
    output_lines = []
    output_lines.append(f"{labels['source']}: {result.source_text} ({language_names[result.source_language]})")
    output_lines.append(f"{labels['translation']}: {result.translated_text} ({language_names[result.target_language]})")
    output_lines.append("")
    output_lines.append(f"{labels['analysis_header']}:")
    output_lines.append(f"| {labels['word']} | {labels['lemma']} | {labels['part_of_speech']} | {labels['features']} |")
    output_lines.append("|------|-------|---------------|----------|")

    for word, lemma, upos, feats in friendly_rows:
        feats_display = feats if feats else "—"

        # Calculate current row width
        row_base = f"| {word} | {lemma} | {upos} | "
        row_end = " |"
        available_width = 100 - len(row_base) - len(row_end)

        # Wrap features if needed
        if len(feats_display) > available_width:
            # Split features on commas and wrap
            parts = feats_display.split(", ")
            wrapped_lines = []
            current_line = ""

            for part in parts:
                if current_line == "":
                    current_line = part
                elif len(current_line + ", " + part) <= available_width:
                    current_line += ", " + part
                else:
                    wrapped_lines.append(current_line)
                    current_line = part

            if current_line:
                wrapped_lines.append(current_line)

            # Add first line
            output_lines.append(f"| {word} | {lemma} | {upos} | {wrapped_lines[0]} |")
            # Add continuation lines
            for line in wrapped_lines[1:]:
                output_lines.append(f"|      |       |               | {line} |")
        else:
            output_lines.append(f"| {word} | {lemma} | {upos} | {feats_display} |")

    return "\n".join(output_lines)


def format_as_json(result: TranslationResult, output_language: LanguageCode = "en") -> str:
    """Format TranslationResult as JSON."""
    data = {
        "source_text": result.source_text,
        "source_language": result.source_language,
        "translated_text": result.translated_text,
        "target_language": result.target_language,
        "translation_id": result.translation_id,
        "morphological_analysis": [
            {"word": row.word, "lemma": row.lemma, "part_of_speech": row.upos, "features": row.feats}
            for row in result.analysis_rows
        ],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_as_dict_list(result: TranslationResult, output_language: LanguageCode = "en") -> List[dict]:
    """Format TranslationResult as list of dictionaries."""
    return [
        {"word": row.word, "lemma": row.lemma, "part_of_speech": row.upos, "features": row.feats}
        for row in result.analysis_rows
    ]
