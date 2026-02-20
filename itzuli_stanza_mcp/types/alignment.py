"""
Type definitions for the Translation Alignment Visualizer.

These types define the enriched data structure that the frontend consumes.
The pipeline is:

    Raw Stanza output → AnalysisRow[] → (enrichment/curation) → AlignmentData

The transformation from AnalysisRow[] to these types involves:
- Automatic: ID assignment, POS mapping, feature string parsing
- Manual/AI-assisted: morpheme segmentation, cross-language alignment
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class LayerType(str, Enum):
    """The three visualization layers."""

    LEXICAL = "lexical"
    GRAMMATICAL_RELATIONS = "grammatical_relations"
    FEATURES = "features"


class Morpheme(BaseModel):
    """A sub-word morpheme within an agglutinative target token.

    Used for Basque tokens where suffixes carry grammatical meaning,
    e.g. "lagunari" → [lagun (friend), -a (DEF), -ri (DAT)]

    The `id` is used as a ribbon endpoint target. Convention: parent
    token id + letter suffix, e.g. "t1a", "t1b", "t1c".
    """

    id: str
    form: str
    gloss: str


class Token(BaseModel):
    """A single token (word) in either source or target sentence.

    For target language tokens with agglutinative morphology, the
    `morphemes` list segments the token into meaningful sub-units.
    Source language tokens typically have no morpheme segmentation.

    When `morphemes` is populated, ribbon endpoints target morpheme IDs
    rather than the token ID.
    """

    id: str
    form: str
    lemma: str
    pos: str
    features: list[str] = Field(default_factory=list)
    morphemes: list[Morpheme] = Field(default_factory=list)


class TokenizedSentence(BaseModel):
    """A sentence with its language tag, display text, and token analysis."""

    lang: str
    text: str
    tokens: list[Token]


class Alignment(BaseModel):
    """A single mapping between source and target elements within one layer.

    `source` and `target` are lists of IDs — token IDs for source,
    morpheme IDs (or token IDs if no morpheme segmentation) for target.

    Lists rather than single IDs because alignments can be:
    - one-to-one:   ["s2"] → ["t2a"]
    - one-to-many:  ["s1"] → ["t0a", "t1a"]
    - many-to-one:  ["s4", "s5", "s6"] → ["t3a"]
    - many-to-many: ["s2", "s3"] → ["t4a", "t4b"]

    The same alignment may appear in multiple layers if it is relevant
    to more than one analytical dimension.
    """

    source: list[str]
    target: list[str]
    label: str


class AlignmentLayers(BaseModel):
    """The three ribbon layers for a sentence pair.

    lexical: Core meaning mappings (know → ezagutu).
    grammatical_relations: Argument structure (subject, object, indirect object)
        and how English word-order roles map to Basque case morphology.
    features: Morphosyntactic features (tense, aspect, negation, agreement,
        definiteness) and how they redistribute across target morphemes.
    """

    lexical: list[Alignment] = Field(default_factory=list)
    grammatical_relations: list[Alignment] = Field(default_factory=list)
    features: list[Alignment] = Field(default_factory=list)


class SentencePair(BaseModel):
    """A fully annotated, aligned sentence pair ready for visualization.

    This is the core unit of data the frontend consumes. Each SentencePair
    is a curated example with hand-verified (or AI-assisted) alignments
    across all three layers.
    """

    id: str
    source: TokenizedSentence
    target: TokenizedSentence
    layers: AlignmentLayers


class AlignmentData(BaseModel):
    """Top-level container for all sentence pairs served to the frontend.

    Serialized as JSON and served from /api/sentences (or loaded as
    fixture data during development).
    """

    sentences: list[SentencePair]
