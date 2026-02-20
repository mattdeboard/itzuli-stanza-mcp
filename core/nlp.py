from typing import List, Tuple

import stanza

from core.types import AnalysisRow, LanguageCode


def create_pipeline(language: LanguageCode = "eu") -> stanza.Pipeline:
    return stanza.Pipeline(
        language, download_method=stanza.DownloadMethod.REUSE_RESOURCES, processors="tokenize,pos,lemma"
    )


def process_raw_analysis(pipeline: stanza.Pipeline, input_text: str) -> List[AnalysisRow]:
    """Process text with Stanza and return raw analysis data."""
    doc = pipeline(input_text)
    rows = []

    for sent in doc.sentences:
        for word in sent.words:
            # Return raw Stanza data: word text, lemma, UPOS, features
            feats = word.feats if word.feats else ""
            rows.append(AnalysisRow(word.text, word.lemma, word.upos, feats))

    return rows


def rows_to_dicts(rows: List[Tuple[str, str, str, str]]) -> List[dict]:
    return [{"word": word, "lemma": lemma, "upos": upos, "feats": feats} for word, lemma, upos, feats in rows]


def print_table(rows: List[Tuple[str, str, str, str]]) -> None:
    word_width = max(len(r[0]) for r in rows)
    lemma_width = max(len(r[1]) for r in rows)
    upos_width = max(len(r[2]) for r in rows)
    for word, lemma, upos, feats in rows:
        line = f"  {word:<{word_width}}  {lemma:<{lemma_width}}  {upos:<{upos_width}}"
        if feats:
            line += f"  — {feats}"
        print(line)


def print_json(rows: List[Tuple[str, str, str, str]]) -> None:
    import json

    print(json.dumps(rows_to_dicts(rows), ensure_ascii=False, indent=2))
