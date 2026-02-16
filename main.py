import stanza

### For the glossing feature, you need these four:
# 1. Tokenization & Sentence Segmentation — splits the text into
# individual words. Foundation for everything else.
# 2. Multi-Word Token (MWT) Expansion — this one's important for Basque
# specifically. Agglutinative forms sometimes need to be expanded into
# their component parts before analysis. Without this, some tokens won't
# get properly decomposed.
# 3. Part-of-Speech & Morphological Features — the core of what you
# need.  This is what gave you PART, AUX, VERB, NOUN and all those
# feature strings like Number[abs]=Plur|Person[erg]=1.
# 4. Lemmatization — gives you the dictionary/base form of each word. So
#   - ditut → ukan (to have)
#   - ezagutzen → ezagutu (to know)
#   - abestiak → abesti (song) This is essential for the gloss line —
# you want to show the root meaning, not the inflected form.
#
# Dependency Parsing is a "nice to have" — it tells you the grammatical
# relationships between words (which word is the subject, which is the
# object, what modifies what). Could be useful for a more advanced view
# or for helping align the English translation to the Basque tokens. But
# it's not required for basic glossing.
###


FRIENDLY_FEATS = {
    "Polarity=Neg": "negation",
    "Mood=Ind": "indicative mood",
    "Number[abs]=Plur": "plural obj",
    "Number[abs]=Sing": "singular obj",
    "Number[erg]=Sing": "singular sub",
    "Number[erg]=Plur": "plural sub",
    "Person[abs]=1": "1per obj (me/us)",
    "Person[abs]=2": "2per obj (you)",
    "Person[abs]=3": "3per obj (it/them)",
    "Person[erg]=1": "1per sub (I)",
    "Person[erg]=2": "2per sub (you)",
    "Person[erg]=3": "3per sub (he/she/it)",
    "VerbForm=Fin": "conjugated",
    "VerbForm=Inf": "infinitive/base form",
    "Aspect=Imp": "habitual/ongoing",
    "Aspect=Perf": "completed act",
    "Case=Abs": "absolutive (sub/obj)",
    "Case=Erg": "ergative (transitive sub)",
    "Case=Dat": "dative (indir obj)",
    # possessive
    "Case=Gen": "genitive",
    "Case=Loc": "locative",
    "Case=Ine": "inessive (inside/within)",
    "Definite=Def": "definite (the)",
    "Definite=Ind": "indefinite (a/an)",
    "Number=Plur": "plural",
    "Number=Sing": "singular",
}

QUIRKS = {"euskal": "combining prefix"}


def create_pipeline():
    # stanza.download("eu", download_method=stanza.DownloadMethod.REUSE_RESOURCES)
    return stanza.Pipeline("eu", download_method=stanza.DownloadMethod.REUSE_RESOURCES, processors="tokenize,pos,lemma")


def rows_to_dicts(rows):
    return [{"word": word, "lemma": lemma, "feats": feats} for word, lemma, feats in rows]


def process_input(pipeline, input_text):
    doc = pipeline(input_text)
    rows = []
    for sent in doc.sentences:
        for word in sent.words:
            descs = []
            quirk = QUIRKS.get(word.text.lower())
            if quirk:
                descs.append(quirk)
            elif word.feats:
                for feat in word.feats.split("|"):
                    friendly = FRIENDLY_FEATS.get(feat)
                    if friendly:
                        descs.append(friendly)
            rows.append((word.text, f"({word.lemma})", ", ".join(descs)))

    return rows


def print_table(rows):
    word_width = max(len(r[0]) for r in rows)
    lemma_width = max(len(r[1]) for r in rows)
    for word, lemma, feats in rows:
        line = f"  {word:<{word_width}}  {lemma:<{lemma_width}}"
        if feats:
            line += f"  — {feats}"
        print(line)


def print_json(rows):
    import json
    print(json.dumps(rows_to_dicts(rows), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="text to process")
    parser.add_argument("--format", choices=["table", "json", "quiet"], default="table", help="output format (quiet suppresses output)")
    args = parser.parse_args()
    rows = process_input(create_pipeline(), args.text)
    if args.format == "json":
        print_json(rows)
    elif args.format == "table":
        print_table(rows)
