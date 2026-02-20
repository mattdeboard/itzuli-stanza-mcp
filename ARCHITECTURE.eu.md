# Arkitektura Dokumentazioa

[🇺🇸 English](ARCHITECTURE.md) | [🔴⚪🟢 Euskera](ARCHITECTURE.eu.md)

Dokumentu honek itzuli-stanza-mcp proiektuaren arkitekturaren ikuspegi osoa eskaintzen du.

## Proiektuaren Ikuspegi Orokorra

Euskal hizkuntzaren prozesamendu sistema bat da, Itzuli APIaren itzulpen gaitasunak eta Stanford-en Stanza liburutegiko analisi morfologiko zehatza konbinatzen dituena. Sistemak AI laguntzaileen integraziorako MCP (Model Context Protocol) zerbitzaria eskaintzen du, itzulpena eta analisi linguistikoa interfaze bakardun batean eskainiz.

## Proiektuaren Egitura

```code
itzuli_stanza_mcp/
├── itzuli_mcp_server.py   # Analisi morfologikoarekin itzulpena eskaintzen duen MCP zerbitzaria
├── services.py            # MCP-rentzako itsaste geruza
├── workflow.py            # Itzulpen eta analisi workflow nagusia (berrerabilgarria)
├── formatters.py          # Irteera formatuak (markdown, JSON, dict lista)
├── nlp.py                 # Stanza pipelinearen konfigurazioa eta testu prozesamendu logika
├── i18n.py                # Lokalizaturiko irteeraren nazioartekotze datuak
└── __init__.py
tests/
├── test_itzuli_mcp_server.py
├── test_workflow.py       # Workflow nagusiaren funtzionalitaterako probak
├── test_formatters.py     # Irteera formatuetarako probak
└── __init__.py
pyproject.toml             # Proiektuaren dependentziak eta konfigurazioa
README.md                  # Erabiltzaile dokumentazioa
CLAUDE.md                  # Garapen gidalerroak
```

## Osagai Nagusiak

### 1. Itzulpen Zerbitzua (`itzuli_mcp_server.py`)

- **Teknologia**: FastMCP duen MCP (Model Context Protocol) zerbitzaria
- **Helburua**: AI laguntzaileen itzulpen eta analisi morfologiko konbinatua
- **Garraioa**: stdio
- **Autentifikazioa**: `ITZULI_API_KEY` ingurumen aldagaia behar du
- **Dependentziak**: koordinazio prozesurako `services.py`

### 2. Workflow Modulua Nagusia (`workflow.py`)

- **Helburua**: Itzulpen + analisiaren berrerabilgarriak diren negozio logika nagusia
- **Eredua**: Egituraturiko datuak itzultzen dituzten funtzio garbitak
- **Funtzio Nagusia**: `process_translation_with_analysis()` - Itzuli + Stanza koordinatzen ditu
- **Diseinua**: Framework-agnostikoa, MCP testuingurutik kanpo erabil daiteke
- **Mendekotasunak**: Itzuli API, Stanza pipeline, NLP prozesatzea

### 3. Irteera Formatu Modulua (`formatters.py`)

- **Helburua**: Itzulpen emaitzen irteera formatu anitzak
- **Funtzioak**:
  - `format_as_markdown_table()` - 100 zutabeko orratzarekin formatutako taula
  - `format_as_json()` - Datu guztiak dituen JSON irteera
  - `format_as_dict_list()` - Erabilera programatikorako Python hiztegirik
- **Diseinua**: Workflow emaitza egituratuak onartzen dituzten funtzio garbitak

### 4. Zerbitzu Koordinazio Geruza (`services.py`)

- **Helburua**: workflow + formatua konbinatzen dituen MCP-rentzako itsaste geruza
- **Eredua**: MCP zerbitzariarentzako wrapper funtzio meheak
- **Funtzioak**: `translate_with_analysis`, `get_quota`, `send_feedback`
- **Diseinua**: Dauden MCP tresnen atzeranzko bateragarritasuna mantentzen du

### 5. NLP Prozesamendu Modulua (`nlp.py`)

- **Teknologia**: Stanford Stanza liburutegia
- **Helburua**: Euskal hizkuntzaren prozesamendu eta ezaugarri ateratze
- **Pipeline**: tokenizazioa, POS etiketatua, lematizazioa
- **Ezaugarriak**: Ohartapen linguistikoen ezaugarri-mapa lagungarria

### 6. Nazioartekotze Modulua (`i18n.py`)

- **Helburua**: Etiketak eta hizkuntza izenak lokalizatuak
- **Hizkuntzak**: Ingelesa, euskera, gaztelania, frantsesa
- **Datuak**: Irteera etiketak, hizkuntza izenak, ezaugarri deskribapen lagungarriak
- **Erabilera**: Hainbat hizkuntzatan lokalizaturiko analisi irteerak onartzen ditu

## Sistemaren Arkitektura

```code
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  MCP Bezeroa    │───▶│  MCP Zerbitzaria │───▶│  Zerbitzu Geruza │
│ (AI Laguntzailea)│    │    (stdio)       │    │  (MCP itsaste)   │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                                                        │
                                                        ▼
                                                ┌──────────────────┐
                                                │ Workflow Modulua │
                                                │ (Logika Nagusia) │
                                                └──────────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              ▼                         ▼                         ▼
                   ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
                   │  Itzuli API      │       │ Stanza Pipeline  │       │ Formatuak        │
                   │ (Itzulpena)      │       │   (Analisia)     │       │ (Mota Anitzak)   │
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

- **Helburua**: Euskal analisi morfologikoa
- **Modeloa**: Aurre-entrenatutako euskal hizkuntza modeloa
- **Deskarga Estrategia**: Lehendik dauden baliabideak berrerabili
- **Prozesatzaileak**: tokenizazioa, pos, lemma

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

## Hedapena

### MCP Zerbitzaria

```bash
ITZULI_API_KEY=zure-gakoa uv run python -m itzuli_stanza_mcp.itzuli_mcp_server
```

## Etorkizuneko Kontuan hartu beharrekoak

- Testu anitzeko batch prozesamendu gehitzea kontuan hartu
- Maiztasunez analizatutako testuetarako cache geruza potentziala
- Itzuli APIak euskarria zabaltzen badu hizkuntza bikote gehigarriak
- Irteera formatu gehigarriak (XML, CSV, etab.) erraz gehitu daitezke
- Workflow moduluak itzulpen soiletik edo analisi soilerako erabilera kasuen tresna banandu eraikitzea ahalbidetzen du

## Glosarioa

- **MCP**: Model Context Protocol - AI laguntzaileen tresna integrazioaren estandarra
- **Stanza**: Hizkuntza anitzeko testu analisiaren Stanford NLP liburutegia
- **Itzuli**: Euskal Gobernuaren itzulpen API ofiziala
- **Analisi Morfologikoa**: Hitzak haien osagai gramatikaletan zatitzea
- **Lematizazioa**: Hitzen oinarri/hiztegi forma aurkitzea
