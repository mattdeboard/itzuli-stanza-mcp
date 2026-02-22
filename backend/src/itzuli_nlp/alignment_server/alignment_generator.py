"""Service for generating alignment data from scaffold using Claude API."""

import logging
from typing import List

from ..core.types import AnalysisRow
from .claude_client import ClaudeClient
from .types import AlignmentData, SentencePair, AlignmentLayers

logger = logging.getLogger(__name__)


def generate_alignments_for_scaffold(scaffold_data: AlignmentData, claude_api_key: str = None) -> AlignmentData:
    """
    Generate alignment layers for scaffold data using Claude API.
    
    Args:
        scaffold_data: AlignmentData with empty alignment layers
        claude_api_key: Optional Claude API key (uses env var if not provided)
    
    Returns:
        AlignmentData with populated alignment layers
    """
    try:
        claude_client = ClaudeClient(api_key=claude_api_key)
        
        enriched_sentences = []
        for sentence_pair in scaffold_data.sentences:
            # Convert tokens to dict format for Claude
            source_tokens = [token.model_dump() for token in sentence_pair.source.tokens]
            target_tokens = [token.model_dump() for token in sentence_pair.target.tokens]
            
            # Generate alignments using Claude
            alignment_layers = claude_client.generate_alignments(
                source_tokens=source_tokens,
                target_tokens=target_tokens,
                source_lang=sentence_pair.source.lang,
                target_lang=sentence_pair.target.lang,
                source_text=sentence_pair.source.text,
                target_text=sentence_pair.target.text
            )
            
            # Create enriched sentence pair
            enriched_pair = SentencePair(
                id=sentence_pair.id,
                source=sentence_pair.source,
                target=sentence_pair.target,
                layers=alignment_layers
            )
            
            enriched_sentences.append(enriched_pair)
            logger.info(f"Generated alignments for sentence: {sentence_pair.id}")
        
        return AlignmentData(sentences=enriched_sentences)
        
    except Exception as e:
        logger.error(f"Alignment generation failed: {e}")
        # Return original scaffold on failure
        return scaffold_data


def create_enriched_alignment_data(
    source_analysis: List[AnalysisRow],
    target_analysis: List[AnalysisRow],
    source_lang: str,
    target_lang: str,
    source_text: str,
    target_text: str,
    sentence_id: str,
    claude_api_key: str = None
) -> AlignmentData:
    """
    Create complete alignment data with Claude-generated alignments.
    
    Args:
        source_analysis: Analysis of source text
        target_analysis: Analysis of target text  
        source_lang: Source language code
        target_lang: Target language code
        source_text: Original source text
        target_text: Translated text
        sentence_id: Unique ID for sentence pair
        claude_api_key: Optional Claude API key
    
    Returns:
        AlignmentData with populated alignment layers
    """
    # Import here to avoid circular imports
    from .scaffold import create_scaffold_from_dual_analysis
    
    # First create scaffold
    scaffold_data = create_scaffold_from_dual_analysis(
        source_analysis=source_analysis,
        target_analysis=target_analysis,
        source_lang=source_lang,
        target_lang=target_lang,
        source_text=source_text,
        target_text=target_text,
        sentence_id=sentence_id
    )
    
    # Then enrich with Claude-generated alignments
    return generate_alignments_for_scaffold(scaffold_data, claude_api_key)