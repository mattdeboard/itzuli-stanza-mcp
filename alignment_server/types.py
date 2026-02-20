"""
Type definitions for the Translation Alignment Visualizer.

These types define the enriched data structure that the frontend consumes.
The pipeline is:

    Raw Stanza output → AnalysisRow[] → (enrichment/curation) → AlignmentData

The transformation from AnalysisRow[] to these types involves:
- Automatic: ID assignment, POS mapping, feature string parsing
- Manual/AI-assisted: cross-language alignment

"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class LayerType(str, Enum):
    """The three visualization layers."""

    LEXICAL = "lexical"
    GRAMMATICAL_RELATIONS = "grammatical_relations"
    FEATURES = "features"


class Token(BaseModel):
    """A single token (word) in either source or target sentence.

    Tokens are the atomic unit for alignment — ribbon endpoints
    target token IDs.
    """

    id: str
    form: str
    lemma: str
    pos: str
    features: list[str] = Field(default_factory=list)


class TokenizedSentence(BaseModel):
    """A sentence with its language tag, display text, and token analysis."""

    lang: str
    text: str
    tokens: list[Token]


class Alignment(BaseModel):
    """A single mapping between source and target tokens within one layer.

    `source` and `target` are lists of token IDs. Lists rather than
    single IDs because alignments can be:
    - one-to-one:   ["s2"] → ["t2"]
    - one-to-many:  ["s1"] → ["t0", "t1"]
    - many-to-one:  ["s4", "s5", "s6"] → ["t3"]
    - many-to-many: ["s2", "s3"] → ["t3", "t4"]

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
