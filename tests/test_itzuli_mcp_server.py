import json
from unittest.mock import patch

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from itzuli_stanza_mcp import itzuli_mcp_server
from itzuli_stanza_mcp.itzuli_mcp_server import translate, get_quota, send_feedback


class TestTranslate:
    def test_returns_translated_text_on_success(self):
        mock_response = {"translatedText": "Hola!", "id": "translation-123"}

        with patch.object(itzuli_mcp_server.client, "getTranslation", return_value=mock_response):
            result = translate("Kaixo!", "eu", "es")

        parsed = json.loads(result)
        assert parsed["translatedText"] == "Hola!"
        assert parsed["id"] == "translation-123"

    def test_raises_tool_error_on_api_failure(self):
        with patch.object(
            itzuli_mcp_server.client,
            "getTranslation",
            side_effect=Exception("Invalid API key or expired"),
        ):
            with pytest.raises(ToolError, match="Translation failed"):
                translate("Kaixo!", "eu", "es")

    def test_rejects_translation_without_basque(self):
        result = translate("Hello!", "en", "es")
        assert "Basque (eu) must be either the source or target language" in result


class TestGetQuota:
    def test_returns_quota_info_on_success(self):
        mock_response = {"remaining": 5000, "total": 10000, "used": 5000}

        with patch.object(itzuli_mcp_server.client, "getQuota", return_value=mock_response):
            result = get_quota()

        parsed = json.loads(result)
        assert parsed["remaining"] == 5000
        assert parsed["total"] == 10000

    def test_raises_tool_error_on_api_failure(self):
        with patch.object(
            itzuli_mcp_server.client,
            "getQuota",
            side_effect=Exception("Invalid status code: 500"),
        ):
            with pytest.raises(ToolError, match="Quota check failed"):
                get_quota()


class TestSendFeedback:
    def test_returns_confirmation_on_success(self):
        mock_response = {"success": True}

        with patch.object(itzuli_mcp_server.client, "sendFeedback", return_value=mock_response):
            result = send_feedback("translation-123", "Hola!", 4)

        parsed = json.loads(result)
        assert parsed["success"] is True

    def test_raises_tool_error_on_api_failure(self):
        with patch.object(
            itzuli_mcp_server.client,
            "sendFeedback",
            side_effect=Exception("Invalid status code: 403"),
        ):
            with pytest.raises(ToolError, match="Feedback submission failed"):
                send_feedback("translation-123", "Hola!", 4)
