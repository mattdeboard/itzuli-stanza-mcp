"""Manual integration test for the complete alignment pipeline.

This test requires actual API keys and is meant to be run manually
to verify the end-to-end functionality works correctly.

Usage:
    ITZULI_API_KEY=your-itzuli-key CLAUDE_API_KEY=your-claude-key \
    uv run python tests/alignment_server/test_integration_manual.py
"""

import os
import json
from pathlib import Path

from itzuli_nlp.alignment_server.alignment_generator import create_enriched_alignment_data
from tools.dual_analysis import analyze_both_texts


def test_end_to_end_pipeline():
    """Test the complete pipeline from text to enriched alignments."""
    
    # Check for required API keys
    itzuli_key = os.environ.get("ITZULI_API_KEY")
    claude_key = os.environ.get("CLAUDE_API_KEY") 
    
    if not itzuli_key or not claude_key:
        print("❌ Missing API keys. Set ITZULI_API_KEY and CLAUDE_API_KEY environment variables.")
        return False
    
    print("🚀 Testing end-to-end alignment generation pipeline...")
    
    # Test cases
    test_cases = [
        {
            "text": "I don't know Basque songs",
            "source_lang": "en",
            "target_lang": "eu",
            "sentence_id": "test-001"
        },
        {
            "text": "Kaixo mundua",
            "source_lang": "eu", 
            "target_lang": "en",
            "sentence_id": "test-002"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test case {i}: '{case['text']}'")
        
        try:
            # Step 1: Perform dual analysis
            print("  🔍 Performing dual analysis...")
            source_analysis, target_analysis, translated_text = analyze_both_texts(
                api_key=itzuli_key,
                text=case["text"],
                source_lang=case["source_lang"],
                target_lang=case["target_lang"]
            )
            
            print(f"  📋 Source tokens: {len(source_analysis)}")
            print(f"  📋 Target tokens: {len(target_analysis)}")
            print(f"  📋 Translation: '{translated_text}'")
            
            # Step 2: Generate enriched alignment data
            print("  🤖 Generating alignments with Claude...")
            alignment_data = create_enriched_alignment_data(
                source_analysis=source_analysis,
                target_analysis=target_analysis,
                source_lang=case["source_lang"],
                target_lang=case["target_lang"],
                source_text=case["text"],
                target_text=translated_text,
                sentence_id=case["sentence_id"],
                claude_api_key=claude_key
            )
            
            # Step 3: Validate results
            sentence_pair = alignment_data.sentences[0]
            layers = sentence_pair.layers
            
            print(f"  ✅ Generated alignments:")
            print(f"    - Lexical: {len(layers.lexical)} alignments")
            print(f"    - Grammatical Relations: {len(layers.grammatical_relations)} alignments") 
            print(f"    - Features: {len(layers.features)} alignments")
            
            # Show some example alignments
            if layers.lexical:
                example = layers.lexical[0]
                print(f"    - Example lexical: {example.source} → {example.target} ({example.label})")
            
            # Save result for inspection
            output_dir = Path("test_output")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"alignment_result_{i}.json"
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(alignment_data.model_dump(), f, indent=2, ensure_ascii=False)
            
            print(f"  💾 Results saved to: {output_file}")
            
        except Exception as e:
            print(f"  ❌ Test case {i} failed: {e}")
            return False
    
    print("\n🎉 All test cases completed successfully!")
    print("\n💡 Check the generated JSON files in test_output/ to inspect alignment quality")
    return True


if __name__ == "__main__":
    success = test_end_to_end_pipeline()
    if not success:
        exit(1)