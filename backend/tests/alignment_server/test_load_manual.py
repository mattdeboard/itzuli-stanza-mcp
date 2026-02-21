#!/usr/bin/env python3
"""Test script for loading alignment data."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from itzuli_nlp.alignment_server.scaffold import load_alignment_data


def main():
    # Load the scaffold we just created
    alignment_data = load_alignment_data("tests/resources/test_scaffold.json")
    
    print("Loaded alignment data:")
    print(f"Number of sentence pairs: {len(alignment_data.sentences)}")
    
    sentence = alignment_data.sentences[0]
    print(f"Sentence ID: {sentence.id}")
    print(f"Source: {sentence.source.text} ({sentence.source.lang})")
    print(f"Target: {sentence.target.text} ({sentence.target.lang})")
    print(f"Source tokens: {len(sentence.source.tokens)}")
    print(f"Target tokens: {len(sentence.target.tokens)}")
    
    # Show token details
    print("\nSource tokens:")
    for token in sentence.source.tokens:
        print(f"  {token.id}: {token.form} ({token.lemma}) [{token.pos}] {token.features}")
    
    print("\nTarget tokens:")
    for token in sentence.target.tokens:
        print(f"  {token.id}: {token.form} ({token.lemma}) [{token.pos}] {token.features}")


if __name__ == "__main__":
    main()