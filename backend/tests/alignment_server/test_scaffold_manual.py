#!/usr/bin/env python3
"""Test script for scaffold generation."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from itzuli_nlp.core.types import AnalysisRow
from itzuli_nlp.alignment_server.scaffold import create_scaffold_from_dual_analysis, save_alignment_data


def main():
    # Sample data from dual analysis
    source_rows = [
        AnalysisRow("Kaixo", "kaixo", "INTJ", ""),
        AnalysisRow("mundua", "mundu", "NOUN", "Case=Abs|Definite=Def|Number=Sing"),
    ]
    
    target_rows = [
        AnalysisRow("Hello", "hello", "INTJ", ""),
        AnalysisRow("world", "world", "NOUN", "Number=Sing"),
    ]
    
    # Generate scaffold
    alignment_data = create_scaffold_from_dual_analysis(
        source_analysis=source_rows,
        target_analysis=target_rows,
        source_lang="eu",
        target_lang="en", 
        source_text="Kaixo mundua",
        target_text="Hello world",
        sentence_id="test-001",
    )
    
    # Save to file
    save_alignment_data(alignment_data, "tests/resources/test_scaffold.json")
    print("Scaffold saved to tests/resources/test_scaffold.json")
    
    # Print sample output
    print("\nGenerated scaffold:")
    print(alignment_data.model_dump_json(indent=2))


if __name__ == "__main__":
    main()