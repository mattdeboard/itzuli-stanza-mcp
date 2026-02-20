# Arkitektura Dokumentazioa

[🇺🇸 English](ARCHITECTURE.md) | [🔴⚪🟢 Euskera](ARCHITECTURE.eu.md)

Dokumentu honek itzuli-nlp proiektuaren arkitekturaren ikuspegi osoa eskaintzen du.

## Proiektuaren Ikuspegi Orokorra

Euskal hizkuntzaren prozesamendu sistema modular bat da, Itzuli APIaren itzulpen gaitasunak eta Stanford-en Stanza liburutegiko analisi morfologiko zehatza konbinatzen dituena. Sistemak berrerabilgarriak diren NLP osagaiak eta AI laguntzaileen integraziorako MCP (Model Context Protocol) zerbitzaria eskaintzen ditu.

## Proiektuaren Egitura

```code
itzuli_nlp/                # Berrerabilgarriak diren NLP liburutegi nagusia
├── workflow.py            # Itzulpen eta analisi workflow nagusia
├── nlp.py                 # Stanza pipeline konfigurazioa eta testu prozesatzea
├── formatters.py          # Irteera formatuak (markdown, JSON, dict lista)
├── types.py               # Partekatutako datu motak (AnalysisRow, TranslationResult)
├── i18n.py                # Lokalizaturiko irteeraren nazioartekotze datuak
└── __init__.py

mcp_server/                # MCP-rentzako kodea
├── server.py              # MCP tresna definizioak eta amaierako puntuak
├── services.py            # MCP itsaste geruza (bilgarri mehea)
└── __init__.py

scripts/                   # Tresna scriptak
├── dual_analysis.py       # Jatorri eta itzulpen testua aztertzen du
├── playground/            # Garapenerako/proba scriptak
│   ├── itzuli_playground.py
│   └── stanza_playground.py
└── __init__.py

tests/                     # Proba sorta
├── test_itzuli_mcp_server.py # MCP zerbitzari probak
├── test_workflow.py       # Workflow nagusi probak
├── test_formatters.py     # Irteera formatu probak
├── test_nlp.py            # NLP prozesamendu probak
└── __init__.py

pyproject.toml             # Proiektuaren dependentziak eta konfigurazioa
README.md                  # Erabiltzaile dokumentazioa
CLAUDE.md                  # Garapen gidalerroak
```

## Osagai Nagusiak

### 1. NLP Liburutegi Nagusia (`itzuli_nlp/`)

**Workflow Modulua (`workflow.py`)**

- **Helburua**: Itzulpen + analisiaren berrerabilgarriak diren negozio logika nagusia
- **Funtzio Nagusia**: `process_translation_with_analysis()` - Itzuli + Stanza koordinatzen ditu
- **Diseinua**: Framework-agnostikoa, egituraturiko `TranslationResult` datuak itzultzen ditu
- **Mendekotasunak**: Itzuli API, Stanza pipeline, NLP prozesatzea

**NLP Prozesamendu Modulua (`nlp.py`)**

- **Teknologia**: Stanford Stanza liburutegia hizkuntza anitzeko euskarriarekin
- **Funtzioak**: `create_pipeline(language)`, `process_raw_analysis()`
- **Pipeline**: tokenizazioa, POS etiketatua, lematizazioa
- **Ezaugarriak**: Stanza irteera gordina mota duten `AnalysisRow` objektu gisa

**Irteera Formatu Modulua (`formatters.py`)**

- **Helburua**: Itzulpen emaitzen irteera formatu anitzeko euskarria
- **Funtzioak**:
  - `format_as_markdown_table()` - 100 zutabeko orratzarekin formatutako taula
  - `format_as_json()` - Datu guztiak dituen JSON irteera
  - `format_as_dict_list()` - Erabilera programatikorako Python hiztegiak
- **Diseinua**: Ezaugarri adiskidetsuen mapeatzearekin funtzio garbitak

**Motak Modulua (`types.py`)**

- **Helburua**: Zirkularriak diren inportazioak saihesteko partekatutako datu egiturak
- **Motak**: `AnalysisRow`, `TranslationResult`, `LanguageCode`
- **Diseinua**: Mota segurtasunerako dataclass sinpleak

**Nazioartekotze Modulua (`i18n.py`)**

- **Helburua**: Lokalizaturiko etiketak eta hizkuntza izenak
- **Hizkuntzak**: Ingelesa, euskera, gaztelania, frantsesa
- **Datuak**: Irteera etiketak, hizkuntza izenak, ezaugarri adiskidetsuen deskribapenak

### 2. MCP Zerbitzaria (`mcp_server/`)

**Zerbitzari Modulua (`server.py`)**

- **Teknologia**: FastMCP duen MCP (Model Context Protocol) zerbitzaria
- **Helburua**: AI laguntzaileen integrazioa itzulpen eta analisi tresnekin
- **Garraioa**: stdio
- **Autentifikazioa**: `ITZULI_API_KEY` ingurumen aldagaia behar du

**Zerbitzu Koordinazio Geruza (`services.py`)**

- **Helburua**: Workflow nagusia + formatua konbinatzen duen MCP-rentzako itsaste geruza
- **Eredua**: MCP zerbitzarirako bilgarri funtzio meheak
- **Funtzioak**: `translate_with_analysis`, `get_quota`, `send_feedback`
- **Diseinua**: Lehendik dauden MCP tresnentzako atzera bateragarritasuna mantentzen du

### 3. Tresna Scriptak (`scripts/`)

**Analisi Bikoitza Scripta (`dual_analysis.py`)**

- **Helburua**: Jatorri eta itzulpen testua pipeline bereiziak erabiliz aztertu
- **Erabilera**: `python -m scripts.dual_analysis "testua" --source eu --target en`
- **Ezaugarriak**: Hizkuntza anitzeko Stanza analisia, JSON/taula irteera
- **Diseinua**: NLP analisi aurreratuaren tresna independentea

## Sistemaren Arkitektura

```code
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  MCP Bezeroa    │───▶│  MCP Zerbitzaria │───▶│ mcp_server/      │
│ (AI Laguntzailea)│    │    (stdio)       │    │ services.py      │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐                           ┌──────────────────┐
│ Zuzeneko Erabil │──────────────────────────▶│ itzuli_nlp/      │
│ (script,app-ak) │                           │ workflow.py      │
└─────────────────┘                           └──────────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              ▼                         ▼                         ▼
                   ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
                   │  Itzuli API      │       │ itzuli_nlp/      │       │ itzuli_nlp/      │
                   │ (Itzulpena)      │       │ nlp.py           │       │ formatters.py    │
                   └──────────────────┘       └──────────────────┘       └──────────────────┘
```

## Datu Fluxua

### Itzulpen Fluxua

1. MCP bezeroak itzulpen tresna deitzen du
2. MCP zerbitzariak hizkuntza bikotea baliozkotzen du (euskera izan behar du)
3. Zerbitzu geruzak workflow modulua deitzen du itzulpen parametroekin
4. Workflow moduluak Itzuli APIa deitzen du itzulpenerako
5. Workflow moduluak euskal testua zehazten du (jatorrizkoa edo itzulitakoa)
6. Workflow moduluak euskal testua Stanza pipeline bidez prozesatzen du
7. Workflow moduluak TranslationResult datu egituratuak itzultzen ditu
8. Zerbitzu geruzak formatu egokia deitzen du (markdown taula MCP-rentzat)
9. Formateatutako emaitza MCP bezeroari itzultzen zaio

### Erabilera Alternatiboa (Workflow Zuzena)

MCP ez diren aplikazioetarako:

1. Aplikazioak `process_translation_with_analysis()` zuzenean deitzen du
2. Workflow-ak TranslationResult egituratu itzultzen du
3. Aplikazioak formatu hautatzen du: markdown, JSON edo dict lista
4. Formateatutako irteera behar den bezala erabiltzen da

## Kanpoko Integrazioak

### Itzuli API

- **Helburua**: Euskal itzulpen zerbitzua
- **Autentifikazioa**: API gakoa ingurumen aldagaien bidez
- **Onartutako Hizkuntzak**: Euskera ↔ Gaztelania, Ingelesa, Frantsesa
- **Erabilitako Amaiera-puntuak**: Itzulpena, kuota egiaztatzea, feedback bidalketa

### Stanford Stanza

- **Helburua**: Hizkuntza anitzeko analisi morfologikoa
- **Modeloak**: Aurre-entrenatutako hizkuntza modeloak (euskera, ingelesa, gaztelania, frantsesa)
- **Deskarga Estrategia**: Lehendik dauden baliabideak berrerabili
- **Prozesatzaileak**: tokenizazioa, pos, lemma (+ mwt hizkuntza batzuentzat)
- **Erabilera**: Analisi zehatzerako hizkuntza bakoitzeko pipeline bereiziak sortzen dira

## Segurtasun Kontuan hartu beharrekoak

- API gakoa ingurumen aldagaietan gordetzen da (ez da kodean sartzen)
- Sarrera baliozkotasuna onartutako hizkuntza bikoteentzat
- Erroreen kudeaketak informazio ihesa saihesten du
- MCP zerbitzaria stdio bidez funtzionatzen du (ez du sare erakusketarik)

## Garapen Inguruna

### Dependentziak

- **Oinarrizkoa**: Stanza, Itzuli, MCP
- **Garapena**: pytest, ruff, anyio
- **Python Bertsioa**: ≥3.10

### Probak

- Proba sorta `tests/` direktorioan
- MCP zerbitzari funtzionalitateari ardazten zaio
- Exekutatu honekin: `pytest`

### Kode Kalitatea

- Ruff bidezko linting
- Type hint-ak aplikagarri denean
- Logging ingurumen aldagaien bidez konfiguratua

## Erabilera

### MCP Zerbitzaria**

```bash
ITZULI_API_KEY=zure-gakoa uv run python -m mcp_server.server
```

### Analisi Bikoitza Scripta**

```bash
uv run python -m scripts.dual_analysis "Kaixo mundua" --source eu --target en --format table
```

## Etorkizuneko Kontuan hartu beharrekoak

- Testu anitzeko batch prozesamendu gehitzea kontuan hartu
- Maiztasunez analizatutako testuetarako cache geruza potentziala
- Itzuli APIak euskarria zabaltzen badu hizkuntza bikote gehigarriak
- Irteera formatu gehigarriak (XML, CSV, etab.) erraz gehitu daitezke
- Egitura modularrak itzulpen soilerako edo analisi soilerako erabilera kasuen tresna banandu eraikitzea ahalbidetzen du
- scripts/ direktorioa tresna gehigarriekin zabaltzea kontuan hartu
- Hizkuntza anitzeko analisi gaitasunak unean onartutako hizkuntzez haratago zabaldu daitezke

## Glosarioa

- **MCP**: Model Context Protocol - AI laguntzaileen tresna integrazioaren estandarra
- **Stanza**: Hizkuntza anitzeko testu analisiaren Stanford NLP liburutegia
- **Itzuli**: Euskal Gobernuaren itzulpen API ofiziala
- **Analisi Morfologikoa**: Hitzak haien osagai gramatikaletan zatitzea
- **Lematizazioa**: Hitzen oinarri/hiztegi forma aurkitzea
