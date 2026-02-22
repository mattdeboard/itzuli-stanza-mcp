# Arkitektura Dokumentazioa

[🇺🇸 English](ARCHITECTURE.md) | [🔴⚪🟢 Euskera](ARCHITECTURE.eu.md)

Dokumentu honek itzuli-nlp proiektuaren arkitekturaren ikuspegi osoa eskaintzen du.

## Proiektuaren Ikuspegi Orokorra

Euskal hizkuntzaren prozesamendu sistema modular bat da, Itzuli APIaren itzulpen gaitasunak eta Stanford-en Stanza liburutegiko analisi morfologiko zehatza konbinatzen dituena. Sistemak berrerabilgarriak diren NLP osagaiak, AI laguntzaileen integraziorako MCP (Model Context Protocol) zerbitzaria eta frontend aplikazioentzako lerrokatze datuak sortzeko HTTP API zerbitzaria eskaintzen ditu.

## Proiektuaren Egitura

```code
src/itzuli_nlp/            # Python pakete nagusia
├── core/                  # Berrerabilgarriak diren NLP liburutegi nagusia
│   ├── workflow.py        # Itzulpen eta analisi workflow nagusia
│   ├── nlp.py             # Stanza pipeline konfigurazioa eta testu prozesatzea
│   ├── formatters.py      # Irteera formatuak (markdown, JSON, dict lista)
│   ├── types.py           # Partekatutako datu motak (AnalysisRow, TranslationResult)
│   ├── i18n.py            # Lokalizaturiko irteeraren nazioartekotze datuak
│   └── __init__.py
├── mcp_server/            # AI laguntzaileen integraziorako MCP-rentzako kodea
│   ├── server.py          # MCP tresna definizioak eta amaierako puntuak
│   ├── services.py        # MCP itsaste geruza (bilgarri mehea)
│   └── __init__.py
├── alignment_server/      # Frontend aplikazioentzako HTTP API
│   ├── server.py          # Cache-arekin FastAPI HTTP zerbitzaria
│   ├── scaffold.py        # Lerrokatze scaffold sortzea
│   ├── claude_client.py   # Lerrokatze sortzearen Claude API integrazioa
│   ├── alignment_generator.py  # Aberasturiko lerrokatze datuen zerbitzu geruza
│   ├── cache.py           # Lerrokatze emaitzen fitxategi-oinarriko JSON cache-a
│   ├── types.py           # Lerrokatze-rentzako Pydantic mota zehatzak
│   └── __init__.py
└── __init__.py

tools/                     # Workflow tresnak eta scriptak
├── dual_analysis.py       # Jatorri eta itzulpen testua aztertzen du
├── generate_scaffold.py   # Analisi bikoitzetik scaffoldak sortu
├── playground/            # Garapenerako/proba scriptak
│   ├── itzuli_playground.py
│   └── stanza_playground.py
└── __init__.py

tests/                     # Osagaiaren arabera antolatutako proba sorta
├── core/                  # Oinarrizko NLP funtzionalitate probak
│   ├── test_workflow.py
│   ├── test_formatters.py
│   ├── test_nlp.py
│   └── __init__.py
├── mcp_server/            # MCP zerbitzari probak
│   ├── test_itzuli_mcp_server.py
│   └── __init__.py
├── alignment_server/      # Lerrokatze zerbitzari probak
│   ├── test_scaffold_manual.py
│   ├── test_load_manual.py
│   └── __init__.py
├── tools/                 # Tresna eta utilitate probak
│   └── __init__.py
├── resources/             # Proba datu fitxategiak
│   └── test_scaffold.json
└── __init__.py

pyproject.toml             # Proiektuaren dependentziak eta konfigurazioa
README.md                  # Erabiltzaile dokumentazioa
CLAUDE.md                  # Garapen gidalerroak
```

## Osagai Nagusiak

### 1. NLP Liburutegi Nagusia (`core/`)

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

### 3. Lerrokatze Zerbitzaria (`alignment_server/`)

**HTTP API Zerbitzaria (`server.py`)**

- **Teknologia**: HTTP REST APIrako FastAPI
- **Helburua**: Frontend aplikazioentzako aberasturiko lerrokatze datuak sortu
- **Amaiera-puntuak**: `/analyze`, `/analyze-and-scaffold`, `/health`
- **Ezaugarriak**: Claude API integrazioa, fitxategi-oinarriko cache-a, lerrokatze datu osoen sortzea
- **Diseinua**: Cache-lehentasunarekin REST API hizkuntza bikoitzeko analisiaren eta IA bidezko lerrokatze sortzearen

**Scaffold Sortzea Modulua (`scaffold.py`)**

- **Helburua**: Analisi bikoitzaren irteera lerrokatze scaffoldetan bihurtu
- **Funtzioak**: `create_scaffold_from_dual_analysis()`, `load_alignment_data()`, `save_alignment_data()`
- **Diseinua**: Analisi linguistikoa Pydantic motetak jarraitzen dituen egituraturiko lerrokatze datuetan eraldatzen du
- **Irteera**: Frontend bistaratzearentzako JSON lerrokatze datuak prest

**Claude API Bezeroa (`claude_client.py`)**

- **Helburua**: Lerrokatze sortzearen Anthropic-en Claude API integrazioa
- **Teknologia**: Egituraturiko JSON lerrokatze erantzunetarako Claude 3.5 Sonnet
- **Ezaugarriak**: Lexiko, gramatika eta ezaugarri lerrokatzeentzako prompt ingeniaritza
- **Diseinua**: API erantzunetarako fall-back kudeaketa duen JSON parsing sendoa

**Lerrokatze Sortzea Zerbitzua (`alignment_generator.py`)**

- **Helburua**: Scaffold sortzea eta Claude aberastea orkestratzen duen zerbitzu geruza
- **Funtzioak**: `generate_alignments_for_scaffold()`, `create_enriched_alignment_data()`
- **Diseinua**: Scaffold sortzea Claude bidezko lerrokatze geruzeskin konbinatzen du

**Fitxategi-oinarriko Cache-a (`cache.py`)**

- **Helburua**: API dei errepikaturak saihesteko cache iraunkorra
- **Teknologia**: JSON fitxategi biltegiratzea duten SHA256 hash gakoak
- **Ezaugarriak**: Cache hit/miss log-a, konfiguragarria den cache direktorioa
- **Diseinua**: `AlignmentData` objektu osoentzako gako-balio biltegia sinplea

**Lerrokatze Motak Modulua (`types.py`)**

- **Helburua**: Lerrokatze datu egituren Pydantic datu modeloak
- **Motak**: `Token`, `TokenizedSentence`, `SentencePair`, `AlignmentData`
- **Diseinua**: Lerrokatze datuen trukerako baliozkotasun zorrotza

### 4. Workflow Tresnak (`tools/`)

**Analisi Bikoitza Scripta (`dual_analysis.py`)**

- **Helburua**: Jatorri eta itzulpen testua pipeline bereiziak erabiliz aztertu
- **Erabilera**: `python -m tools.dual_analysis "testua" --source eu --target en`
- **Ezaugarriak**: Hizkuntza anitzeko Stanza analisia, JSON/taula irteera
- **Diseinua**: NLP analisi aurreratuaren tresna independentea

**Scaffold Sortzea Scripta (`generate_scaffold.py`)**

- **Helburua**: Analisi bikoitzaren irteeratik lerrokatze scaffoldak sortu
- **Erabilera**: `python -m tools.generate_scaffold "testua" --source eu --target en`
- **Ezaugarriak**: Testu sarreratik amaiera arte scaffolds sortzea
- **Diseinua**: Analisi bikoitza scaffold sorrerarkin konbinatzen du

## Sistemaren Arkitektura

```code
                    BEZERO INTERFAZEAK
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  MCP Bezeroa    │  │ Frontend App    │  │  Zuzeneko Erabil│
│(AI Laguntzailea)│  │ (Lerrokatze UI) │  │ (script,tresnak)│
└─────────┬───────┘  └─────────┬───────┘  └─────────┬───────┘
          │                    │                    │
          ▼                    ▼                    │
┌─────────────────┐  ┌─────────────────┐            │
│  MCP Zerbitz.   │  │  HTTP Zerbitz.  │            │
│    (stdio)      │  │   (8000 portua) │            │
└─────────┬───────┘  └─────────┬───────┘            │
          │                    │                    │
          ▼                    ▼                    │
┌─────────────────┐  ┌─────────────────┐            │
│ mcp_server/     │  │ alignment_server│            │
│ services.py     │  │ server.py       │            │
└─────────┬───────┘  └─────────┬───────┘            │
          │                    │                    │
          └────────┬───────────┘                    │
                   │                                │
                   └───────────┬────────────────────┘
                               ▼
               PARTEKATUTAKO NEGOZIO LOGIKA
              ┌─────────────────────────────┐
              │ core/workflow.py            │
              │ tools/dual_analysis.py      │
              └─────────────┬───────────────┘
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Itzuli API     │ │ core/nlp.py     │ │ core/           │
│ (Itzulpena)     │ │ (Stanza)        │ │ formatters.py   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
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

### HTTP API Fluxua (Lerrokatze Zerbitzaria)

Frontend aplikazioak lerrokatze datuak sortzerakoan:

1. Frontend aplikazioak HTTP POST egiten du `/analyze-and-scaffold`-era
2. `alignment_server/server.py`-k eskaera jasotzen du testu eta hizkuntza parametroekin
3. Zerbitzariak `tools.dual_analysis.analyze_both_texts()` deitzen du analisi bikoitzerako
4. Analisi bikoitzak jatorri eta xede hizkuntzarentzako pipeline bereiziak sortzen ditu
5. Jatorri eta itzulpen testua pipeline egokien bidez prozesatzen dira
6. Zerbitzariak `alignment_server.scaffold.create_scaffold_from_dual_analysis()` deitzen du
7. Scaffold sorreak analisi emaitzak lerrokatze datu egituraretan bihurtzen ditu
8. Pydantic baliozkotasunak datuak `AlignmentData` eskemari jarraitzen zaizkiola ziurtatzen du
9. JSON erantzuna frontend aplikazioari itzultzen zaio

### Erabilera Alternatiboa (Workflow Zuzena)

MCP ez diren aplikazioetarako:

1. Aplikazioak `core.workflow` edo `core.nlp` zuzenean inportatzen du
2. Oinarrizko funtzioak deitzen ditu `process_translation_with_analysis()` bezalakoak
3. Egituraturiko datuak jasotzen ditu (`TranslationResult`, `List[AnalysisRow]`)
4. Aplikazioak formatu hautatzen du: markdown, JSON edo dict lista
5. Formateatutako irteera behar den bezala erabiltzen da

### Analisi Bikoitza Fluxua (tools/dual_analysis.py)

1. Scriptak Itzuli API deitzen du itzulpenerako
2. Jatorri eta xede hizkuntzarentzako Stanza pipeline bereiziak sortzen ditu
3. Jatorri eta itzulpen testua pipeline egokien bidez prozesatzen ditu
4. Hizkuntza bakoitzerako `List[AnalysisRow]` bereiziak itzultzen ditu
5. Bi testuen analisi morfologikoa erakusten duen irteera formateatzen du

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
uv run python -m tools.dual_analysis "Kaixo mundua" --source eu --target en --format table
```

### Lerrokatze Zerbitzaria

```bash
uv run python -m alignment_server.server
```

## Etorkizuneko Kontuan hartu beharrekoak

- Testu anitzeko batch prozesamendu gehitzea kontuan hartu
- Maiztasunez analizatutako testuetarako cache geruza potentziala
- Itzuli APIak euskarria zabaltzen badu hizkuntza bikote gehigarriak
- Irteera formatu gehigarriak (XML, CSV, etab.) erraz gehitu daitezke
- Egitura modularrak itzulpen soilerako edo analisi soilerako erabilera kasuen tresna banandu eraikitzea ahalbidetzen du
- tools/ direktorioa tresna gehigarriekin zabaltzea kontuan hartu
- Lerrokatze zerbitzariak esaldi bikote anitzarentzako batch scaffold sorrera euskarri dezake
- HTTP APIari autentifikazioa eta abiadura mugaketa gehitzea kontuan hartu
- Denbora errealeko lerrokatze kolaboraziorako WebSocket euskarriaren potentziala
- Hizkuntza anitzeko analisi gaitasunak unean onartutako hizkuntzez haratago zabaldu daitezke

## Glosarioa

- **MCP**: Model Context Protocol - AI laguntzaileen tresna integrazioaren estandarra
- **Stanza**: Hizkuntza anitzeko testu analisiaren Stanford NLP liburutegia
- **Itzuli**: Euskal Gobernuaren itzulpen API ofiziala
- **Analisi Morfologikoa**: Hitzak haien osagai gramatikaletan zatitzea
- **Lematizazioa**: Hitzen oinarri/hiztegi forma aurkitzea
