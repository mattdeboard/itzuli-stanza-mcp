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
            logger.info("Calling Claude API for alignment generation")
            response = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=4000,
                temperature=0.1,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            content = response.content[0].text if response.content else ""
            logger.info(f"Claude response received, length: {len(content)}")

            alignments_data = self._parse_alignment_response(content)
            logger.info(f"Parsed alignments - Lexical: {len(alignments_data.get('lexical', []))}, "
                       f"Grammatical: {len(alignments_data.get('grammatical_relations', []))}, "
                       f"Features: {len(alignments_data.get('features', []))}")

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

        return f"""You are a linguist generating translation alignments between {source_lang} and {target_lang} for an interactive visualization tool.

## Sentence pair

Source ({source_lang}): "{source_text}"
Target ({target_lang}): "{target_text}"

## Source tokens
{json.dumps(source_tokens, indent=2)}

## Target tokens
{json.dumps(target_tokens, indent=2)}

## What you are producing

Three layers of alignment, each answering a different analytical question. Alignments map source token IDs to target token IDs. The same mapping MAY appear in multiple layers when relevant to more than one.

---

### LEXICAL layer — "What does this word mean?"

Dictionary-level correspondences. Every content word in the source should have a lexical alignment if a target correspondent exists. Function words (prepositions, determiners, auxiliaries) generally do NOT get lexical alignments — their meaning is structural, not lexical.

Label format:
- Simple: "word → target_word (core meaning)"
- When target is inflected: "word → target_lemma (in 'inflected_form')"
- Compound splits: "compound → target1 + target2 (compound: part1 + part2)"

Common Basque patterns to watch for:
- English compound nouns may split into two Basque tokens (bookstore → liburu denda)
- Basque adjectives follow the noun (new book → liburu berri), but this is word ORDER — the lexical mapping is still new → berri
- The indefinite article "a" maps to "bat" (the numeral "one") — this is lexical

---

### GRAMMATICAL RELATIONS layer — "What role does this word play?"

Maps grammatical roles (subject, direct object, indirect object, oblique/adjunct) to show how English encodes them through word order and prepositions while Basque encodes them through case suffixes and auxiliary verb agreement.

Label format: "role (case): 'source_phrase' → explanation with 'target_form'"

Basque case system — apply these mappings:
- English subject → Basque ERGATIVE (-k) for transitive verbs, ABSOLUTIVE (-a/∅) for intransitive verbs. This split is critical: "I see him" → ergative, but "I go" → absolutive.
- English direct object → Basque ABSOLUTIVE (-a/∅)
- English indirect object / "to [person]" → Basque DATIVE (-ri)
- English "to [place]" / directional motion → Basque ALLATIVE (-ra)
- English "with" (accompaniment) → Basque COMITATIVE (-rekin)
- English "in" / "at" (location) → Basque INESSIVE (-n)
- English "to [verb]" (purpose) → Basque ALLATIVE (-ra) on nominalized verb

Auxiliary agreement — Basque auxiliaries agree with subject, object, AND indirect object simultaneously:
- Transitive verb → uses "edun" (dut, nuen, nion, etc.) and subject is ergative
- Intransitive verb → uses "izan" (naiz, da, etc.) and subject is absolutive
- When a source pronoun (I, him, her, them) has no separate Basque pronoun, it is still encoded as agreement in the auxiliary. Map the source pronoun to the auxiliary token.
- Ditransitive verbs (give, show, tell) → auxiliary agrees with ALL THREE arguments. Each agreement relationship is a separate alignment.

---

### FEATURES layer — "Where does grammatical meaning hide?"

Shows how grammatical features that occupy one location in English redistribute across Basque morphology. This is the most detailed layer. A single source token may generate multiple feature alignments.

Label format: "feature_name: 'source_form' → 'target_form' (explanation)"

Systematic features to check for EVERY sentence:

TENSE/ASPECT:
- English tense (past, present, future) → encoded in Basque auxiliary (naiz/nintzen, dut/nuen)
- English progressive "is going" → Basque prospective -ko/-go or progressive ari
- English perfective "gave" → Basque perfective participle
- English imperfective/habitual "know" → Basque imperfective -tzen

NEGATION:
- English "don't/doesn't/didn't/not" → Basque "ez" (separate particle) PLUS may affect auxiliary. Split into two alignments: one for the negation particle, one for the auxiliary function.

AGREEMENT:
- Every English pronoun that maps to agreement in the Basque auxiliary gets a features alignment for person/number agreement, IN ADDITION TO its grammatical relations alignment. These are separate concerns: grammatical relations says "this is the subject," features says "the auxiliary encodes 1st person singular."

DEFINITENESS:
- English "the" → Basque -a suffix (fused into case suffixes: -ak, -ari, -aren, etc.)
- English "a" → Basque "bat" (numeral, postposed) or bare noun
- Note: definiteness markers in Basque are often fused with case suffixes on the same word. E.g., "dendara" = denda + -a (DEF) + -ra (ALL). Point the alignment at the whole word since we don't segment morphemes.

CASE AS FEATURE:
- When an English preposition maps to a Basque case suffix, create a features alignment: "case_name: 'preposition' → '-suffix' in 'inflected_form'"
- This is in ADDITION to the grammatical relations alignment for the same mapping. Grammatical relations says "this is the indirect object (dative)," features says "the preposition 'to' maps to the dative suffix -ri."

POSSESSION:
- English "my/your/his/her" → Basque genitive form (nire, zure, bere) if explicit
- Sometimes possession is implicit in Basque (e.g., "amarekin" = with mom, where "my" is understood from context). Note this as an alignment with an explicit label about implicit possession.

WORD ORDER:
- If adjective position reverses (English pre-nominal → Basque post-nominal), note this in features.

---

## Output format

Return ONLY a JSON object with this structure, no other text:

{{
  "lexical": [
    {{"source": ["s0"], "target": ["t1"], "label": "..."}}
  ],
  "grammatical_relations": [
    {{"source": ["s0", "s1"], "target": ["t2"], "label": "..."}}
  ],
  "features": [
    {{"source": ["s0"], "target": ["t1"], "label": "..."}}
  ]
}}

Use only token IDs from the provided lists. Do not include any text outside the JSON object."""

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