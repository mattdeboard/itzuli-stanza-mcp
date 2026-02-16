"""Service layer for coordinating Itzuli translations with Stanza morphological analysis."""

import logging

from Itzuli import Itzuli
from itzuli_stanza_mcp.nlp import create_pipeline, process_input

logger = logging.getLogger("itzuli-stanza-services")

LANGUAGE_NAMES = {
    "eu": "Basque",
    "es": "Spanish", 
    "en": "English",
    "fr": "French",
}

# Module-level lazy-loaded singletons
def get_stanza_pipeline():
    """Get or create Stanza pipeline (cached)."""
    if not hasattr(get_stanza_pipeline, '_pipeline'):
        get_stanza_pipeline._pipeline = create_pipeline()
    return get_stanza_pipeline._pipeline


def translate_with_analysis(api_key: str, text: str, source_language: str, target_language: str) -> str:
    """Translate text and provide morphological analysis of Basque text."""
    # Get translation from Itzuli
    itzuli_client = Itzuli(api_key)
    translation_data = itzuli_client.getTranslation(text, source_language, target_language)
    translated_text = translation_data.get("translation", "")
    
    # Determine which text to analyze (always analyze Basque text)
    basque_text = text if source_language == "eu" else translated_text
    
    # Perform morphological analysis
    stanza_pipeline = get_stanza_pipeline()
    rows = process_input(stanza_pipeline, basque_text)
    
    # Format output with 100-column limit
    output_lines = []
    output_lines.append(f"Source: {text} ({LANGUAGE_NAMES[source_language]})")
    output_lines.append(f"Translation: {translated_text} ({LANGUAGE_NAMES[target_language]})")
    output_lines.append("")
    output_lines.append("Morphological Analysis:")
    output_lines.append("| Word | Lemma | Features |")
    output_lines.append("|------|-------|----------|")
    
    for word, lemma, feats in rows:
        feats_display = feats if feats else "—"
        
        # Calculate current row width
        row_base = f"| {word} | {lemma} | "
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
            output_lines.append(f"| {word} | {lemma} | {wrapped_lines[0]} |")
            # Add continuation lines
            for line in wrapped_lines[1:]:
                output_lines.append(f"|      |       | {line} |")
        else:
            output_lines.append(f"| {word} | {lemma} | {feats_display} |")
    
    return "\n".join(output_lines)


def get_quota(api_key: str):
    """Check API quota using Itzuli client."""
    itzuli_client = Itzuli(api_key)
    return itzuli_client.getQuota()


def send_feedback(api_key: str, translation_id: str, correction: str, evaluation: int):
    """Send feedback using Itzuli client."""
    itzuli_client = Itzuli(api_key)
    return itzuli_client.sendFeedback(translation_id, correction, evaluation)