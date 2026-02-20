# itzuli-nlp

[🇺🇸 English](README.md) | [🔴⚪🟢 Euskera](README.eu.md)

Euskal hizkuntzaren prozesamendu tresna-sorta bat da, [Itzuli](https://www.euskadi.eus/itzuli/) APIaren itzulpen gaitasunak eta [Stanza](https://stanfordnlp.github.io/stanza/)ren bidezko analisi morfologiko zehatza konbinatzen dituena. Sistemak berrerabilgarriak diren NLP osagaiak eta IA laguntzaileen integraziorako MCP zerbitzaria eskaintzen ditu.

## Ikuspegi orokorra

Proiektu honek bi zerbitzu osagarri eskaintzen ditu:

1. **Itzuli Itzulpen Zerbitzua** — Euskal Gobernuaren itzulpen API ofiziala euskera ↔ gaztelania/ingelesa/frantsesera itzulpen kalitatetsuetarako
2. **Stanza Analisi Morfologikoa** — Stanford NLP tresna-sorta euskal testuaren banaketa gramatikala, lematizazioa, POS etiketatua eta ezaugarri linguistikoak eskaintzen dituena

Zerbitzuak independenteki edo batera erabil daitezke euskal hizkuntzaren prozesamendu osatuetarako.

## Proiektuaren egitura

Egitura osoaren xehetasunetarako ikus [ARCHITECTURE.eu.md](./ARCHITECTURE.eu.md).

```code
itzuli_nlp/              # Berrerabilgarriak diren NLP liburutegi nagusia
  workflow.py            # Itzulpen eta analisi workflow nagusia
  nlp.py                 # Stanza pipeline eta testu prozesatzea
  formatters.py          # Irteera formatuak (markdown, JSON, dict lista)
  types.py               # Partekatutako datu motak
  i18n.py                # Nazioartekotze datuak

mcp_server/              # MCP-rentzako kodea
  server.py              # MCP tresna definizioak
  services.py            # MCP itsaste geruza

scripts/                 # Tresna scriptak
  dual_analysis.py       # Jatorri eta itzulpen testua aztertzen du
  playground/            # Garapenerako/proba scriptak
```

## Berrerabilgarriak diren Osagaiak

Itzulpen eta analisi funtzionalitate nagusia MCP zerbitzariaz haratago berrerabilgarria izateko diseinatu da:

- **`itzuli_nlp.workflow`** — `process_translation_with_analysis()` funtzio nagusia dauka, edozein Python aplikazioan modu independentean erabil daitekeena. Egituraturiko `TranslationResult` datuak itzultzen ditu.

- **`itzuli_nlp.nlp`** — Analisi morfologikorako `process_raw_analysis()` eta hizkuntza anitzeko Stanza pipelineentzako `create_pipeline()` eskaintzen ditu.

- **`itzuli_nlp.formatters`** — Itzulpen emaitzen irteera formatu anitzak:
  - `format_as_markdown_table()` — 100 zutabeko orratzarekin formatutako taula
  - `format_as_json()` — Itzulpen eta analisi datu guztiak dituen JSON irteera
  - `format_as_dict_list()` — Erabilera programatikorako Python hiztegi zerrenda

- **`scripts/dual_analysis.py`** — Jatorri eta itzulpen testua aztertzen duen tresna scripta, hizkuntza bakoitzerako Stanza pipeline bereiziak erabiliz.

Egitura modular honek itzuli+stanza funtzionalitatea beste aplikazioetan integratzea ahalbidetzen du NLP logika nagusiaren eta MCP zerbitzari arduren artean banaketa garbia mantentzen duen bitartean.

## Itzuli Itzulpen MCP Zerbitzaria

Model Context Protocol bidez itzulpena eta analisi morfologikoa eskaintzen ditu. Itzulpen bakoitzak automatikoki Stanford-en [Stanza pipeline neuronal](https://stanfordnlp.github.io/stanza/neural_pipeline.html)a erabiliz euskal testuaren analisi gramatiko zehatza barne hartzen du.

### API Gakoaren Konfigurazioa

Itzuli itzulpen zerbitzua erabiltzeko, API gako bat behar duzu:

1. API gako bat eskatu [https://itzuli.vicomtech.org/en/api/](https://itzuli.vicomtech.org/en/api/) helbidean
2. `ITZULI_API_KEY` ingurumen aldagaia ezarri

stdio garraio bidez funtzionatzen du.

```bash
ITZULI_API_KEY=zure-gakoa uv run python -m mcp_server.server
```

### Tresna Scriptak

**Analisi Bikoitza Scripta** — Jatorri eta itzulpen testua aztertu:

```bash
# Euskal jatorria eta ingeles itzulpena aztertu
uv run python -m scripts.dual_analysis "Kaixo mundua" --source eu --target en --format table

# Erabilera programatikorako JSON irteera
uv run python -m scripts.dual_analysis "Hello world" --source en --target eu --format json
```

### Tresnak

- **translate** — Itzuli API ofiziala erabiliz euskerara edo euskeratik testua itzuli. Onartutako bikoteak: eu<->es, eu<->en, eu<->fr. Aukerako `output_language` parametroak 'en', 'eu', 'es', 'fr' onartzen ditu taula goiburuen lokalizaziorako.
- **get_quota** — Uneko API erabilera kuota egiaztatu.
- **send_feedback** — Aurreko itzulpen baterako zuzentzaile edo ebaluazioa bidali.

### AI Laguntzaileekin Erabilera

AI laguntzaileekin lan egitean MCP zerbitzari honetara sarbidea dutenean, irteera hizkuntzaren hobespenak zaindu ahal dituzu modu askotan:

**Itzulpen gonbiteekin irteera hizkuntzaren hobespena erabiliz:**

```text
@en@eu Hello, mesedez itzuli hau euskerara eta erakutsi analisia euskeraz
```

**Euskal irteerarako argibide zuzena:**

```text
Itzuli "Hello" ingelesetik euskerara output_language="eu" erabiliz analisi taulak euskal goiburuak erakuts ditzan
```

**Saiorako hizkuntza hobespena ezarriz:**

```text
Elkarrizketa honetako itzulpen guztietarako, mesedez erabili output_language="eu" analisi morfologikoa euskeraz erakusteko
```

**Tresna erabilera zuzenaren zehaztapena:**

```python
translate(text="Kaixo", source_language="eu", target_language="en", output_language="eu")
```

`output_language` parametroak analisi morfologikoaren taula goiburu eta etiketen hizkuntza kontrolatzen du, ez itzulpenaren norabidea.

### Irteeraren adibidea

Analisi morfologiko automatikoa duen itzulpena:

```text
Jatorria: No conozco las canciones vascas (Spanish)
Itzulpena: Ez ditut ezagutzen euskal abestiak (Basque)

Analisi Morfologikoa:
| Hitza     | Lema    | Hitz Mota          | Ezaugarriak                                 |
| --------- | ------- | ------------------ | ------------------------------------------- |
| Ez        | ez      | partikulaa         | ezeztapena                                  |
| ditut     | ukan    | aditz laguntzailea | adierazpen modua, objektu plurala,          |
|           |         |                    | subjektu singularra, 3. pertsona obj,       |
|           |         |                    | 1. pertsona subj (nik)                      |
| ezagutzen | ezagutu | aditza             | ohikoa/jarraian                             |
| euskal    | euskal  | adjektiboa         | konbinazio aurrizkia                        |
| abestiak  | abesti  | izena              | absolutiboa (nor), mugatu (-a/-ak), plurala |
```
