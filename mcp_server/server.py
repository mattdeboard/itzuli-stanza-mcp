import json
import logging
import os
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from mcp_server import services
from core.types import LanguageCode
from core.i18n import LANGUAGE_NAMES

load_dotenv()

LOG_LEVEL = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO), stream=sys.stderr)
logger = logging.getLogger("itzuli-mcp")

SUPPORTED_LANGUAGES = ("eu", "es", "en", "fr")

api_key = os.environ.get("ITZULI_API_KEY", "")

mcp = FastMCP("itzuli-mcp")


@mcp.tool()
def translate(
    text: str, source_language: LanguageCode, target_language: LanguageCode, output_language: LanguageCode = "en"
) -> str:
    """Translate text to or from Basque with morphological analysis. Basque must be either the source or target language. Supported pairs: eu<->es, eu<->en, eu<->fr. Output can be localized to 'en', 'eu', 'es', or 'fr'."""
    if source_language not in SUPPORTED_LANGUAGES or target_language not in SUPPORTED_LANGUAGES:
        return f"Unsupported language. Supported: {', '.join(SUPPORTED_LANGUAGES)}"

    if source_language != "eu" and target_language != "eu":
        return "Basque (eu) must be either the source or target language. Supported pairs: eu<->es, eu<->en, eu<->fr."

    logger.debug("translate request: %s -> %s, text=%s", source_language, target_language, text)
    try:
        result = services.translate_with_analysis(api_key, text, source_language, target_language, output_language)
        return result
    except Exception as e:
        raise ToolError(f"Translation with analysis failed: {e}") from e


@mcp.tool()
def get_quota() -> str:
    """Check the current API usage quota for the Itzuli translation service."""
    logger.debug("get_quota request")
    try:
        data = services.get_quota(api_key)
    except Exception as e:
        raise ToolError(f"Quota check failed: {e}") from e
    logger.debug("get_quota response: %s", data)
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
def send_feedback(translation_id: str, correction: str, evaluation: int) -> str:
    """Submit feedback or a correction for a previous translation."""
    logger.debug("send_feedback request: id=%s", translation_id)
    try:
        data = services.send_feedback(api_key, translation_id, correction, evaluation)
    except Exception as e:
        raise ToolError(f"Feedback submission failed: {e}") from e
    logger.debug("send_feedback response: %s", data)
    return json.dumps(data, ensure_ascii=False, indent=2)


def _register_prompt(from_lang: str, to_lang: str) -> None:
    from_name = LANGUAGE_NAMES["en"][from_lang]
    to_name = LANGUAGE_NAMES["en"][to_lang]

    @mcp.prompt(
        name=f"{from_lang}@{to_lang}",
        description=f"Translate text from {from_name} to {to_name}",
    )
    def prompt(text: str) -> str:
        return f"Translate the following {from_name} text to {to_name} using the translate tool, then return only the translated text.\n\n{text}"


for other in [lang for lang in SUPPORTED_LANGUAGES if lang != "eu"]:
    _register_prompt("eu", other)
    _register_prompt(other, "eu")


if __name__ == "__main__":
    logger.debug("itzuli-mcp server running on stdio")
    mcp.run(transport="stdio")
