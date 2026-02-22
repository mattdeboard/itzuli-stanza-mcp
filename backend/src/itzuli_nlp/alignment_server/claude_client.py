"""Claude API client for generating alignment data."""

import json
import logging
import os
from typing import Dict, Any

import anthropic
from anthropic import Anthropic

from .types import AlignmentLayers, Alignment

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for interacting with Claude API to generate alignment data."""
    
    def __init__(self, api_key: str | None = None):
        """Initialize Claude client with API key."""
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY environment variable or api_key parameter required")
        
        self.client = Anthropic(api_key=self.api_key)
    
    def generate_alignments(
        self,
        source_tokens: list[Dict[str, Any]],
        target_tokens: list[Dict[str, Any]], 
        source_lang: str,
        target_lang: str,
        source_text: str,
        target_text: str
    ) -> AlignmentLayers:
        """Generate all three alignment layers using Claude."""
        
        prompt = self._build_alignment_prompt(
            source_tokens, target_tokens, source_lang, target_lang, source_text, target_text
        )
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            content = response.content[0].text if response.content else ""
            alignments_data = self._parse_alignment_response(content)
            
            return AlignmentLayers(
                lexical=alignments_data.get("lexical", []),
                grammatical_relations=alignments_data.get("grammatical_relations", []),
                features=alignments_data.get("features", [])
            )
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return AlignmentLayers()
    
    def _build_alignment_prompt(
        self,
        source_tokens: list[Dict[str, Any]],
        target_tokens: list[Dict[str, Any]],
        source_lang: str,
        target_lang: str,
        source_text: str,
        target_text: str
    ) -> str:
        """Build structured prompt for alignment generation."""
        
        return f"""Generate translation alignments between {source_lang} and {target_lang} tokens.

Source text: "{source_text}"
Target text: "{target_text}"

Source tokens:
{json.dumps(source_tokens, indent=2)}

Target tokens:  
{json.dumps(target_tokens, indent=2)}

Generate alignments for three layers:

1. **Lexical**: Core meaning mappings between words/morphemes
2. **Grammatical Relations**: How grammatical roles (subject, object, etc.) map across languages
3. **Features**: How morphosyntactic features (tense, number, case, etc.) are expressed

Return ONLY a JSON object with this structure:
{{
  "lexical": [
    {{"source": ["s0"], "target": ["t1"], "label": "greeting"}},
    {{"source": ["s1"], "target": ["t0", "t2"], "label": "world+definiteness"}}
  ],
  "grammatical_relations": [
    {{"source": ["s1"], "target": ["t0"], "label": "direct_object"}}
  ],
  "features": [
    {{"source": ["s1"], "target": ["t2"], "label": "definiteness"}}
  ]
}}

Guidelines:
- Use token IDs from the provided lists (s0, s1, etc. for source; t0, t1, etc. for target)
- Alignments can be one-to-one, one-to-many, many-to-one, or many-to-many
- Labels should be descriptive but concise
- Focus on linguistically meaningful alignments
- Empty layers are acceptable if no alignments exist"""

    def _parse_alignment_response(self, content: str) -> Dict[str, list[Alignment]]:
        """Parse Claude's JSON response into alignment objects."""
        try:
            # Extract JSON from response (Claude might include explanation text)
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON found in Claude response")
                return {"lexical": [], "grammatical_relations": [], "features": []}
            
            json_str = content[json_start:json_end]
            data = json.loads(json_str)
            
            # Convert to Alignment objects
            result = {}
            for layer_name in ["lexical", "grammatical_relations", "features"]:
                alignments = []
                for item in data.get(layer_name, []):
                    alignments.append(Alignment(
                        source=item["source"],
                        target=item["target"], 
                        label=item["label"]
                    ))
                result[layer_name] = alignments
            
            return result
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to parse Claude response: {e}")
            return {"lexical": [], "grammatical_relations": [], "features": []}