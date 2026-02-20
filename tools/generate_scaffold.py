#!/usr/bin/env python3
"""
Generate alignment scaffolds from dual analysis.

This script takes text input, performs dual analysis, and generates 
a scaffold JSON file ready for manual alignment annotation.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from tools.dual_analysis import analyze_both_texts
from alignment_server.scaffold import create_scaffold_from_dual_analysis, save_alignment_data

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Generate alignment scaffold from text")
    parser.add_argument("text", help="Text to translate and create scaffold for")
    parser.add_argument("--source", "-s", required=True, choices=["eu", "es", "en", "fr"], help="Source language")
    parser.add_argument("--target", "-t", required=True, choices=["eu", "es", "en", "fr"], help="Target language")
    parser.add_argument("--output", "-o", required=True, help="Output JSON file path")
    parser.add_argument("--id", help="Sentence ID (defaults to generated ID)")
    parser.add_argument("--api-key", help="Itzuli API key (or set ITZULI_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("ITZULI_API_KEY")
    if not api_key:
        logger.error("API key required. Set ITZULI_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # Generate sentence ID if not provided
    sentence_id = args.id or f"{args.source}-{args.target}-{hash(args.text) % 10000:04d}"
    
    try:
        logger.info(f"Performing dual analysis: {args.source} -> {args.target}")
        translated_text, source_analysis, target_analysis = analyze_both_texts(
            api_key=api_key,
            text=args.text,
            source_language=args.source,
            target_language=args.target,
        )
        
        logger.info("Generating alignment scaffold")
        alignment_data = create_scaffold_from_dual_analysis(
            source_analysis=source_analysis,
            target_analysis=target_analysis,
            source_lang=args.source,
            target_lang=args.target,
            source_text=args.text,
            target_text=translated_text,
            sentence_id=sentence_id,
        )
        
        # Save scaffold
        save_alignment_data(alignment_data, args.output)
        logger.info(f"Scaffold saved to {args.output}")
        
        # Show summary
        sentence = alignment_data.sentences[0]
        print(f"\\nScaffold generated for: {sentence.id}")
        print(f"Source: {sentence.source.text} ({sentence.source.lang}) - {len(sentence.source.tokens)} tokens")
        print(f"Target: {sentence.target.text} ({sentence.target.lang}) - {len(sentence.target.tokens)} tokens")
        print(f"Ready for alignment annotation in: {args.output}")
        
    except Exception as e:
        logger.error(f"Scaffold generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()