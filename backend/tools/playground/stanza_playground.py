#!/usr/bin/env python3
"""Stanza playground for testing Basque morphological analysis."""

import sys
from itzuli_stanza_mcp.nlp import create_pipeline


def main():
    if len(sys.argv) < 2:
        print("Usage: python stanza_playground.py <basque_sentence>")
        print("Example: python stanza_playground.py 'Kaixo mundua!'")
        sys.exit(1)

    sentence = " ".join(sys.argv[1:])

    print(f"Processing: {sentence}")
    print("-" * 50)

    # Create pipeline using the same configuration as services.py
    pipeline = create_pipeline()

    # Print the final processor pipeline output
    for sent in pipeline(sentence).sentences:
        for word in sent.words:
            print(f"Text: {word.text}")
            print(f"Lemma: {word.lemma}")
            print(f"UPOS: {word.upos}")
            print(f"XPOS: {word.xpos}")
            print(f"Features: {word.feats}")
            print("-" * 30)


if __name__ == "__main__":
    main()
