"""Tests for alignment cache functionality."""

import json
import tempfile
from pathlib import Path
import pytest

from itzuli_nlp.alignment_server.cache import AlignmentCache
from itzuli_nlp.alignment_server.types import AlignmentData, SentencePair, TokenizedSentence, Token, AlignmentLayers


class TestAlignmentCache:
    """Test alignment caching functionality."""
    
    def test_cache_key_generation(self):
        """Test that cache keys are consistent."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = AlignmentCache(cache_dir=temp_dir)
            
            key1 = cache._get_cache_key("Hello", "en", "eu")
            key2 = cache._get_cache_key("Hello", "en", "eu")
            key3 = cache._get_cache_key("Hello world", "en", "eu")
            
            assert key1 == key2  # Same inputs = same key
            assert key1 != key3  # Different inputs = different keys
            assert len(key1) == 64  # SHA256 hex string
    
    def test_cache_miss(self):
        """Test cache miss returns None."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = AlignmentCache(cache_dir=temp_dir)
            
            result = cache.get("Hello", "en", "eu")
            assert result is None
    
    def test_cache_set_and_get(self):
        """Test storing and retrieving cache data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = AlignmentCache(cache_dir=temp_dir)
            
            # Create test alignment data
            test_data = AlignmentData(
                sentences=[
                    SentencePair(
                        id="test-001",
                        source=TokenizedSentence(
                            lang="en",
                            text="Hello",
                            tokens=[Token(id="s0", form="Hello", lemma="hello", pos="intj", features=[])]
                        ),
                        target=TokenizedSentence(
                            lang="eu", 
                            text="Kaixo",
                            tokens=[Token(id="t0", form="Kaixo", lemma="kaixo", pos="intj", features=[])]
                        ),
                        layers=AlignmentLayers()
                    )
                ]
            )
            
            # Store in cache
            cache.set("Hello", "en", "eu", test_data)
            
            # Retrieve from cache
            result = cache.get("Hello", "en", "eu")
            
            assert result is not None
            assert isinstance(result, AlignmentData)
            assert len(result.sentences) == 1
            assert result.sentences[0].source.text == "Hello"
            assert result.sentences[0].target.text == "Kaixo"
    
    def test_cache_file_created(self):
        """Test that cache files are created on disk."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = AlignmentCache(cache_dir=temp_dir)
            
            test_data = AlignmentData(sentences=[])
            cache.set("test", "en", "eu", test_data)
            
            cache_dir = Path(temp_dir)
            json_files = list(cache_dir.glob("*.json"))
            
            assert len(json_files) == 1
            assert json_files[0].suffix == ".json"
            
            # Verify file contains valid JSON
            content = json_files[0].read_text()
            data = json.loads(content)
            assert "sentences" in data
    
    def test_cache_clear(self):
        """Test clearing all cached data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = AlignmentCache(cache_dir=temp_dir)
            
            # Create multiple cache entries
            test_data = AlignmentData(sentences=[])
            cache.set("test1", "en", "eu", test_data)
            cache.set("test2", "en", "es", test_data)
            
            cache_dir = Path(temp_dir)
            assert len(list(cache_dir.glob("*.json"))) == 2
            
            # Clear cache
            cache.clear()
            
            assert len(list(cache_dir.glob("*.json"))) == 0
    
    def test_cache_directory_creation(self):
        """Test that cache directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "nested" / "cache"
            assert not cache_path.exists()
            
            cache = AlignmentCache(cache_dir=str(cache_path))
            assert cache_path.exists()
            assert cache_path.is_dir()
    
    def test_corrupted_cache_file_handling(self):
        """Test graceful handling of corrupted cache files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = AlignmentCache(cache_dir=temp_dir)
            
            # Create corrupted cache file
            cache_key = cache._get_cache_key("test", "en", "eu")
            cache_path = cache._get_cache_path(cache_key)
            cache_path.write_text("invalid json content")
            
            # Should return None for corrupted file
            result = cache.get("test", "en", "eu")
            assert result is None