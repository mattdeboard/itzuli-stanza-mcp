/**
 * TypeScript types matching the Python Pydantic models from
 * backend/src/itzuli_nlp/alignment_server/types.py
 *
 * These types define the data structure for the translation alignment visualizer.
 */

/**
 * Supported language codes from backend/src/itzuli_nlp/core/types.py
 * Maps to Python: LanguageCode = Literal["eu", "en", "es", "fr"]
 */
export enum LanguageCode {
  EU = 'eu', // Basque
  EN = 'en', // English
  ES = 'es', // Spanish
  FR = 'fr', // French
}

/**
 * The three visualization layers.
 */
export enum LayerType {
  LEXICAL = 'lexical',
  GRAMMATICAL_RELATIONS = 'grammatical_relations',
  FEATURES = 'features',
}

/**
 * A single token (word) in either source or target sentence.
 *
 * Tokens are the atomic unit for alignment — ribbon endpoints
 * target token IDs.
 */
export type Token = {
  id: string
  form: string
  lemma: string
  pos: string
  features: string[]
}

/**
 * A sentence with its language tag, display text, and token analysis.
 */
export type TokenizedSentence = {
  lang: LanguageCode
  text: string
  tokens: Token[]
}

/**
 * A single mapping between source and target tokens within one layer.
 *
 * `source` and `target` are lists of token IDs. Lists rather than
 * single IDs because alignments can be:
 * - one-to-one:   ["s2"] → ["t2"]
 * - one-to-many:  ["s1"] → ["t0", "t1"]
 * - many-to-one:  ["s4", "s5", "s6"] → ["t3"]
 * - many-to-many: ["s2", "s3"] → ["t3", "t4"]
 *
 * The same alignment may appear in multiple layers if it is relevant
 * to more than one analytical dimension.
 */
export type Alignment = {
  source: string[]
  target: string[]
  label: string
}

/**
 * The three ribbon layers for a sentence pair.
 *
 * lexical: Core meaning mappings (know → ezagutu).
 * grammatical_relations: Argument structure (subject, object, indirect object)
 *     and how English word-order roles map to Basque case morphology.
 * features: Morphosyntactic features (tense, aspect, negation, agreement,
 *     definiteness) and how they redistribute across target morphemes.
 */
export type AlignmentLayers = {
  lexical: Alignment[]
  grammatical_relations: Alignment[]
  features: Alignment[]
}

/**
 * A fully annotated, aligned sentence pair ready for visualization.
 *
 * This is the core unit of data the frontend consumes. Each SentencePair
 * is a curated example with hand-verified (or AI-assisted) alignments
 * across all three layers.
 */
export type SentencePair = {
  id: string
  source: TokenizedSentence
  target: TokenizedSentence
  layers: AlignmentLayers
}

/**
 * Top-level container for all sentence pairs served to the frontend.
 *
 * Serialized as JSON and served from /api/sentences (or loaded as
 * fixture data during development).
 */
export type AlignmentData = {
  sentences: SentencePair[]
}

/**
 * Configuration for data source (fixture vs API)
 */
export type DataSourceConfig = {
  useFixtures: boolean
  apiBaseUrl?: string
}

/**
 * Hook return type for alignment data loading
 */
export type UseAlignmentDataResult = {
  data: AlignmentData | null
  loading: boolean
  error: string | null
  refetch: () => void
}
