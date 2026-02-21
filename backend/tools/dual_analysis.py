#!/usr/bin/env python3
"""
Script for performing NLP analysis on both source and translated text.

This script translates text using Itzuli and then performs morphological analysis 
on both the original source text and the translation, returning separate 
AnalysisRow arrays for each.
"""

import argparse
import json
import logging
import os
import sys
from typing import Tuple, List

from dotenv import load_dotenv
from Itzuli import Itzuli

from itzuli_nlp.core.nlp import create_pipeline, process_raw_analysis
from itzuli_nlp.core.types import AnalysisRow, LanguageCode

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Cache pipelines to avoid recreating them
_pipelines = {}


def get_cached_pipeline(language: LanguageCode):
    """Get or create a Stanza pipeline for the specified language."""
    if language not in _pipelines:
        logger.info(f"Creating Stanza pipeline for language: {language}")
        _pipelines[language] = create_pipeline(language)
    return _pipelines[language]


def analyze_both_texts(
    api_key: str,
    text: str,
    source_language: LanguageCode,
    target_language: LanguageCode,
) -> Tuple[str, List[AnalysisRow], List[AnalysisRow]]:
    """
    Translate text and analyze both source and translated text.
    
    Args:
        api_key: Itzuli API key
        text: Source text to translate
        source_language: Source language code
        target_language: Target language code
        
    Returns:
        Tuple of (translated_text, source_analysis, translation_analysis)
    """
    # Get translation
    itzuli_client = Itzuli(api_key)
    translation_data = itzuli_client.getTranslation(text, source_language, target_language)
    translated_text = translation_data.get("translated_text", "")
    
    logger.info(f"Translation: '{text}' -> '{translated_text}'")
    
    # Get pipelines for both languages
    source_pipeline = get_cached_pipeline(source_language)
    target_pipeline = get_cached_pipeline(target_language)
    
    # Analyze source text
    source_analysis = process_raw_analysis(source_pipeline, text)
    logger.info(f"Source analysis: {len(source_analysis)} tokens")
    
    # Analyze translated text
    translation_analysis = process_raw_analysis(target_pipeline, translated_text)
    logger.info(f"Translation analysis: {len(translation_analysis)} tokens")
    
    return translated_text, source_analysis, translation_analysis


def format_analysis_output(
    source_text: str,
    translated_text: str,
    source_language: LanguageCode,
    target_language: LanguageCode,
    source_analysis: List[AnalysisRow],
    translation_analysis: List[AnalysisRow],
    output_format: str = "json"
) -> str:
    """Format the dual analysis results."""
    
    if output_format == "json":
        return json.dumps({
            "source": {
                "text": source_text,
                "language": source_language,
                "analysis": [
                    {
                        "word": row.word,
                        "lemma": row.lemma,
                        "upos": row.upos,
                        "feats": row.feats
                    }
                    for row in source_analysis
                ]
            },
            "translation": {
                "text": translated_text,
                "language": target_language,
                "analysis": [
                    {
                        "word": row.word,
                        "lemma": row.lemma,
                        "upos": row.upos,
                        "feats": row.feats
                    }
                    for row in translation_analysis
                ]
            }
        }, indent=2, ensure_ascii=False)
    
    elif output_format == "table":
        output = []
        output.append(f"Source: {source_text} ({source_language})")
        output.append("Source Analysis:")
        output.append("| Word | Lemma | UPOS | Features |")
        output.append("|------|-------|------|----------|")
        for row in source_analysis:
            output.append(f"| {row.word} | {row.lemma} | {row.upos} | {row.feats or '—'} |")
        
        output.append("")
        output.append(f"Translation: {translated_text} ({target_language})")
        output.append("Translation Analysis:")
        output.append("| Word | Lemma | UPOS | Features |")
        output.append("|------|-------|------|----------|")
        for row in translation_analysis:
            output.append(f"| {row.word} | {row.lemma} | {row.upos} | {row.feats or '—'} |")
        
        return "\n".join(output)
    
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def main():
    parser = argparse.ArgumentParser(description="Analyze both source and translated text")
    parser.add_argument("text", help="Text to translate and analyze")
    parser.add_argument("--source", "-s", required=True, choices=["eu", "es", "en", "fr"], help="Source language")
    parser.add_argument("--target", "-t", required=True, choices=["eu", "es", "en", "fr"], help="Target language")
    parser.add_argument("--format", "-f", default="json", choices=["json", "table"], help="Output format")
    parser.add_argument("--api-key", help="Itzuli API key (or set ITZULI_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.environ.get("ITZULI_API_KEY")
    if not api_key:
        logger.error("API key required. Set ITZULI_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    try:
        translated_text, source_analysis, translation_analysis = analyze_both_texts(
            api_key=api_key,
            text=args.text,
            source_language=args.source,
            target_language=args.target,
        )
        
        output = format_analysis_output(
            source_text=args.text,
            translated_text=translated_text,
            source_language=args.source,
            target_language=args.target,
            source_analysis=source_analysis,
            translation_analysis=translation_analysis,
            output_format=args.format
        )
        
        print(output)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()