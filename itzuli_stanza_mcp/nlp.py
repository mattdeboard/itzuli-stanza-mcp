from typing import List, Tuple, Literal

import stanza

from itzuli_stanza_mcp.i18n import FRIENDLY_FEATS, FRIENDLY_UPOS, QUIRKS

LanguageCode = Literal["eu", "en", "es", "fr"]


def create_pipeline() -> stanza.Pipeline:
    return stanza.Pipeline("eu", download_method=stanza.DownloadMethod.REUSE_RESOURCES, processors="tokenize,pos,lemma")


def rows_to_dicts(rows: List[Tuple[str, str, str, str]]) -> List[dict]:
    return [{"word": word, "lemma": lemma, "upos": upos, "feats": feats} for word, lemma, upos, feats in rows]


def process_input(
    pipeline: stanza.Pipeline, input_text: str, language: LanguageCode = "en"
) -> List[Tuple[str, str, str, str]]:
    doc = pipeline(input_text)
    rows = []
    friendly_feats = FRIENDLY_FEATS.get(language, FRIENDLY_FEATS["en"])
    friendly_upos = FRIENDLY_UPOS.get(language, FRIENDLY_UPOS["en"])
    quirks = QUIRKS.get(language, QUIRKS["en"])

    for sent in doc.sentences:
        for word in sent.words:
            descs = []
            quirk = quirks.get(word.text.lower())
            if quirk:
                descs.append(quirk)
            elif word.feats:
                for feat in word.feats.split("|"):
                    friendly = friendly_feats.get(feat, feat)
                    if friendly:
                        descs.append(friendly)

            upos_friendly = friendly_upos.get(word.upos, word.upos)
            rows.append((word.text, f"({word.lemma})", upos_friendly, ", ".join(descs)))

    return rows


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
