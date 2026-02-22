"""Tests for Claude API integration."""

import json
import os
from unittest.mock import Mock, patch
import pytest

from itzuli_nlp.alignment_server.claude_client import ClaudeClient
from itzuli_nlp.alignment_server.types import AlignmentLayers, Alignment


class TestClaudeClient:
    """Test Claude API client functionality."""
    
    def test_init_with_api_key(self):
        """Test client initialization with explicit API key."""
        client = ClaudeClient(api_key="test-key")
        assert client.api_key == "test-key"
    
    def test_init_without_api_key_raises_error(self):
        """Test that missing API key raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="CLAUDE_API_KEY"):
                ClaudeClient()
    
    def test_init_with_env_var(self):
        """Test client initialization with environment variable."""
        with patch.dict(os.environ, {"CLAUDE_API_KEY": "env-key"}):
            client = ClaudeClient()
            assert client.api_key == "env-key"
    
    @patch('itzuli_nlp.alignment_server.claude_client.Anthropic')
    def test_generate_alignments_success(self, mock_anthropic):
        """Test successful alignment generation."""
        # Mock Claude API response
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = '''
        {
            "lexical": [
                {"source": ["s0"], "target": ["t0"], "label": "greeting"}
            ],
            "grammatical_relations": [],
            "features": [
                {"source": ["s1"], "target": ["t1"], "label": "definiteness"}
            ]
        }
        '''
        mock_response.content = [mock_content]
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Test data
        source_tokens = [{"id": "s0", "form": "Hello"}, {"id": "s1", "form": "world"}]
        target_tokens = [{"id": "t0", "form": "Kaixo"}, {"id": "t1", "form": "mundua"}]
        
        client = ClaudeClient(api_key="test-key")
        result = client.generate_alignments(
            source_tokens=source_tokens,
            target_tokens=target_tokens,
            source_lang="en",
            target_lang="eu", 
            source_text="Hello world",
            target_text="Kaixo mundua"
        )
        
        assert isinstance(result, AlignmentLayers)
        assert len(result.lexical) == 1
        assert result.lexical[0].source == ["s0"]
        assert result.lexical[0].target == ["t0"] 
        assert result.lexical[0].label == "greeting"
        assert len(result.grammatical_relations) == 0
        assert len(result.features) == 1
    
    @patch('itzuli_nlp.alignment_server.claude_client.Anthropic')
    def test_generate_alignments_api_error(self, mock_anthropic):
        """Test handling of Claude API errors."""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client
        
        source_tokens = [{"id": "s0", "form": "Hello"}]
        target_tokens = [{"id": "t0", "form": "Kaixo"}]
        
        client = ClaudeClient(api_key="test-key")
        result = client.generate_alignments(
            source_tokens=source_tokens,
            target_tokens=target_tokens,
            source_lang="en",
            target_lang="eu",
            source_text="Hello",
            target_text="Kaixo"
        )
        
        # Should return empty alignment layers on error
        assert isinstance(result, AlignmentLayers)
        assert len(result.lexical) == 0
        assert len(result.grammatical_relations) == 0
        assert len(result.features) == 0
    
    def test_parse_alignment_response_valid_json(self):
        """Test parsing valid JSON response."""
        client = ClaudeClient(api_key="test-key")
        
        response = '''
        Here's the alignment data:
        {
            "lexical": [
                {"source": ["s0"], "target": ["t0"], "label": "test"}
            ],
            "grammatical_relations": [],
            "features": []
        }
        More explanation text.
        '''
        
        result = client._parse_alignment_response(response)
        
        assert "lexical" in result
        assert len(result["lexical"]) == 1
        assert isinstance(result["lexical"][0], Alignment)
        assert result["lexical"][0].source == ["s0"]
        assert result["lexical"][0].target == ["t0"]
        assert result["lexical"][0].label == "test"
    
    def test_parse_alignment_response_invalid_json(self):
        """Test handling of invalid JSON response."""
        client = ClaudeClient(api_key="test-key")
        
        result = client._parse_alignment_response("Invalid JSON response")
        
        assert result == {"lexical": [], "grammatical_relations": [], "features": []}
    
    def test_build_alignment_prompt(self):
        """Test prompt generation includes required elements."""
        client = ClaudeClient(api_key="test-key")
        
        source_tokens = [{"id": "s0", "form": "Hello"}]
        target_tokens = [{"id": "t0", "form": "Kaixo"}]
        
        prompt = client._build_alignment_prompt(
            source_tokens=source_tokens,
            target_tokens=target_tokens,
            source_lang="en",
            target_lang="eu",
            source_text="Hello",
            target_text="Kaixo"
        )
        
        assert "Hello" in prompt
        assert "Kaixo" in prompt
        assert "lexical" in prompt
        assert "grammatical_relations" in prompt
        assert "features" in prompt
        assert "s0" in prompt
        assert "t0" in prompt