"""Service layer for coordinating Itzuli translations with Stanza morphological analysis."""

import logging

from Itzuli import Itzuli
from core.types import LanguageCode
from core.workflow import process_translation_with_analysis
from core.formatters import format_as_markdown_table

logger = logging.getLogger("itzuli-stanza-services")


def translate_with_analysis(
    api_key: str,
    text: str,
    source_language: LanguageCode,
    target_language: LanguageCode,
    output_language: LanguageCode = "en",
) -> str:
    """Translate text and provide morphological analysis of Basque text with localized output."""
    result = process_translation_with_analysis(api_key, text, source_language, target_language, output_language)
    return format_as_markdown_table(result, output_language)


def get_quota(api_key: str) -> dict:
    """Check API quota using Itzuli client."""
    itzuli_client = Itzuli(api_key)
    return itzuli_client.getQuota()


def send_feedback(api_key: str, translation_id: str, correction: str, evaluation: int) -> dict:
    """Send feedback using Itzuli client."""
    itzuli_client = Itzuli(api_key)
    return itzuli_client.sendFeedback(translation_id, correction, evaluation)
