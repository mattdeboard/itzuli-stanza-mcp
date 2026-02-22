"""File-based JSON cache for alignment data."""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Optional

from .types import AlignmentData

logger = logging.getLogger(__name__)


class AlignmentCache:
    """Simple file-based cache for alignment data."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize cache with directory path."""
        self.cache_dir = Path(cache_dir or os.environ.get("ALIGNMENT_CACHE_DIR", ".cache/alignments"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key from request parameters."""
        key_string = f"{text}:{source_lang}:{target_lang}"
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key."""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[AlignmentData]:
        """Retrieve cached alignment data."""
        try:
            cache_key = self._get_cache_key(text, source_lang, target_lang)
            cache_path = self._get_cache_path(cache_key)
            
            if not cache_path.exists():
                return None
            
            json_content = cache_path.read_text(encoding="utf-8")
            data = json.loads(json_content)
            return AlignmentData.model_validate(data)
            
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None
    
    def set(self, text: str, source_lang: str, target_lang: str, alignment_data: AlignmentData) -> None:
        """Store alignment data in cache."""
        try:
            cache_key = self._get_cache_key(text, source_lang, target_lang)
            cache_path = self._get_cache_path(cache_key)
            
            json_content = alignment_data.model_dump_json(indent=2)
            cache_path.write_text(json_content, encoding="utf-8")
            
            logger.info(f"Cached alignment data for key: {cache_key}")
            
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    def clear(self) -> None:
        """Clear all cached data."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("Cache cleared")
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")