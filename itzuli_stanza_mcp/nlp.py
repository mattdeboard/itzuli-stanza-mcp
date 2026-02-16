import stanza

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
