# itzuli-stanza-mcp

[🇺🇸 English](README.md) | [🔴⚪🟢 Euskera](README.eu.md)

Euskal hizkuntzaren prozesamendu tresna-sorta bat da, [Itzuli](https://www.euskadi.eus/itzuli/) APIaren itzulpen gaitasunak eta [Stanza](https://stanfordnlp.github.io/stanza/)ren bidezko analisi morfologiko zehatza konbinatzen dituena. Sistemak itzulpen zerbitzuak eta analisi linguistikoa eskaintzen ditu MCP zerbitzarietan paketatuta.

## Ikuspegi orokorra

Proiektu honek bi zerbitzu osagarri eskaintzen ditu:

1. **Itzuli Itzulpen Zerbitzua** — Euskal Gobernuaren itzulpen API ofiziala euskera ↔ gaztelania/ingelesa/frantsesera itzulpen kalitatetsuetarako
2. **Stanza Analisi Morfologikoa** — Stanford NLP tresna-sorta euskal testuaren banaketa gramatikala, lematizazioa, POS etiketatua eta ezaugarri linguistikoak eskaintzen dituena

Zerbitzuak independenteki edo batera erabil daitezke euskal hizkuntzaren prozesamendu osatuetarako.

## Proiektuaren egitura

Egitura osoaren xehetasunetarako ikus [ARCHITECTURE.eu.md](./ARCHITECTURE.eu.md).

```code
itzuli_stanza_mcp/
  itzuli_mcp_server.py   # MCP zerbitzaria itzulpena eta analisi morfologikoarekin
  services.py            # Itzuli eta Stanza koordinatzen dituen zerbitzu geruza
  nlp.py                 # Stanza pipelinearen konfigurazioa eta testu prozesamendu
```

## Itzuli Itzulpen MCP Zerbitzaria

Model Context Protocol bidez itzulpena eta analisi morfologikoa eskaintzen ditu. Itzulpen bakoitzak automatikoki Stanford-en [Stanza pipeline neuronal](https://stanfordnlp.github.io/stanza/neural_pipeline.html)a erabiliz euskal testuaren analisi gramatiko zehatza barne hartzen du.

### API Gakoaren Konfigurazioa

Itzuli itzulpen zerbitzua erabiltzeko, API gako bat behar duzu:

1. API gako bat eskatu [https://itzuli.vicomtech.org/en/api/](https://itzuli.vicomtech.org/en/api/) helbidean
2. `ITZULI_API_KEY` ingurumen aldagaia ezarri

stdio garraio bidez funtzionatzen du.

```bash
ITZULI_API_KEY=zure-gakoa uv run python -m itzuli_stanza_mcp.itzuli_mcp_server
```

### Tresnak

- **translate** — Itzuli API ofiziala erabiliz euskerara edo euskeratik testua itzuli. Onartutako bikoteak: eu<->es, eu<->en, eu<->fr.
- **get_quota** — Uneko API erabilera kuota egiaztatu.
- **send_feedback** — Aurreko itzulpen baterako zuzentzaile edo ebaluazioa bidali.

### Irteeraren adibidea

Analisi morfologiko automatikoa duen itzulpena:

```text
Source: No conozco las canciones vascas (Spanish)
Translation: Ez ditut ezagutzen euskal abestiak (Basque)

Morphological Analysis:
| Word      | Lemma     | Features                                                       |
| --------- | --------- | -------------------------------------------------------------- |
| Ez        | (ez)      | negation                                                       |
| ditut     | (ukan)    | indicative mood, plural obj, singular sub, 3per obj (it/them), |
|           |           | 1per sub (I), conjugated                                       |
| ezagutzen | (ezagutu) | habitual/ongoing                                               |
| euskal    | (euskal)  | combining prefix                                               |
| abestiak  | (abesti)  | absolutive (sub/obj), definite (the), plural                   |
```
