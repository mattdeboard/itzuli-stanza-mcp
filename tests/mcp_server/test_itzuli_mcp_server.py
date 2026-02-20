import json
from unittest.mock import patch

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from mcp_server.server import translate, get_quota, send_feedback


class TestTranslate:
    def test_returns_translated_text_on_success(self):

        with patch(
            "mcp_server.services.translate_with_analysis",
            return_value="Source: Kaixo! (euskera)\nTranslation: Hola! (español)\n\nMorphological Analysis:\n| Word | Lemma | Part of Speech | Features |\n|------|-------|---------------|----------|\n| Hola | (hola) | interjection | — |",
        ):
            result = translate("Kaixo!", "eu", "es")

        assert "Kaixo!" in result
        assert "Hola!" in result

    def test_raises_tool_error_on_api_failure(self):
        with patch(
            "mcp_server.services.translate_with_analysis",
            side_effect=Exception("Invalid API key or expired"),
        ):
            with pytest.raises(ToolError, match="Translation with analysis failed"):
                translate("Kaixo!", "eu", "es")

    def test_rejects_translation_without_basque(self):
        result = translate("Hello!", "en", "es")
        assert "Basque (eu) must be either the source or target language" in result

    def test_result_format_has_four_columns(self):
        with patch(
            "mcp_server.services.translate_with_analysis",
            return_value="Source: Kaixo! (euskera)\nTranslation: Hola! (español)\n\nMorphological Analysis:\n| Word | Lemma | Part of Speech | Features |\n|------|-------|---------------|----------|\n| Kaixo | (kaixo) | interjection | Animacy=Inan |",
        ):
            result = translate("Kaixo!", "eu", "es")

        lines = result.split("\n")

        # Assert source section (first line)
        assert lines[0].startswith("Source:")

        # Assert translation section (second line)
        assert lines[1].startswith("Translation:")

        # Assert empty line separator
        assert lines[2] == ""

        # Assert morphological analysis section starts
        assert "Morphological Analysis:" in lines[3]

        # Assert table header exists with exactly four columns
        header_line = [line for line in lines if "| Word | Lemma |" in line][0]
        column_count = header_line.count("|") - 1  # Subtract 1 for leading |
        assert column_count == 4, f"Expected exactly 4 columns, got {column_count}"
        assert "| Word | Lemma | Part of Speech | Features |" in result
        assert "|------|-------|---------------|----------|" in result


class TestGetQuota:
    def test_returns_quota_info_on_success(self):
        mock_response = {"remaining": 5000, "total": 10000, "used": 5000}

        with patch("mcp_server.services.get_quota", return_value=mock_response):
            result = get_quota()

        parsed = json.loads(result)
        assert parsed["remaining"] == 5000
        assert parsed["total"] == 10000

    def test_raises_tool_error_on_api_failure(self):
        with patch(
            "mcp_server.services.get_quota",
            side_effect=Exception("Invalid status code: 500"),
        ):
            with pytest.raises(ToolError, match="Quota check failed"):
                get_quota()


class TestSendFeedback:
    def test_returns_confirmation_on_success(self):
        mock_response = {"success": True}

        with patch("mcp_server.services.send_feedback", return_value=mock_response):
            result = send_feedback("translation-123", "Hola!", 4)

        parsed = json.loads(result)
        assert parsed["success"] is True

    def test_raises_tool_error_on_api_failure(self):
        with patch(
            "mcp_server.services.send_feedback",
            side_effect=Exception("Invalid status code: 403"),
        ):
            with pytest.raises(ToolError, match="Feedback submission failed"):
                send_feedback("translation-123", "Hola!", 4)
