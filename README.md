# itzuli-stanza-mcp

Basque language processing toolkit that combines translation capabilities from the [Itzuli](https://www.euskadi.eus/itzuli/) API with detailed morphological analysis via [Stanza](https://stanfordnlp.github.io/stanza/). The system provides both translation services and enriched linguistic analysis, packaged as HTTP and MCP servers.

## Overview

This project offers two complementary services:

1. **Itzuli Translation Service** — Official Basque government translation API for high-quality Basque ↔ Spanish/English/French translation
2. **Stanza Morphological Analysis** — Stanford NLP toolkit providing detailed grammatical breakdowns of Basque text, including lemmatization, POS tagging, and linguistic features

The services can be used independently or together to provide comprehensive Basque language processing capabilities.

## Project structure

See [ARCHITECTURE.md](./ARCHITECTURE.md) for full details on project structure.

```code
itzuli_stanza_mcp/
  app.py                 # Flask server for Stanza morphological analysis
  nlp.py                 # Stanza pipeline and text processing
  itzuli_mcp_server.py   # MCP server for Itzuli translation
```

## Stanza Morphological Analysis Server

Provides detailed grammatical analysis of Basque text through a Flask HTTP API using Stanford's [Stanza neural pipeline](https://stanfordnlp.github.io/stanza/neural_pipeline.html). The pipeline is configured with tokenization, parts-of-speech (POS), and lemmatization processors.

```bash
uv run python -m itzuli_stanza_mcp.app
```

The server runs on port 5001.

### `POST /stanza`

Analyze Basque text to extract lemmas, parts of speech, and grammatical features:

```bash
curl -X POST http://localhost:5001/stanza \
  -H "Content-Type: application/json" \
  -d '{"text": "Ez ditut ezagutzen euskal abestiak"}'
```

Response includes word-by-word morphological breakdown:

```json
[
  {"word": "Ez", "lemma": "(ez)", "feats": "negation"},
  {"word": "ditut", "lemma": "(ukan)", "feats": "indicative mood, plural obj, singular sub, 3per obj (it/them), 1per sub (I), conjugated"},
  {"word": "ezagutzen", "lemma": "(ezagutu)", "feats": "habitual/ongoing"},
  {"word": "euskal", "lemma": "(euskal)", "feats": "combining prefix"},
  {"word": "abestiak", "lemma": "(abesti)", "feats": "absolutive (sub/obj), definite (the), plural"}
]
```

## Itzuli Translation MCP Server

Provides access to the official Basque government translation service through the Model Context Protocol. Itzuli serves as the authoritative source for high-quality Basque translations, which can be enriched with morphological analysis from the Stanza server.

### API Key Setup

To use the Itzuli translation service, you need an API key:

1. Apply for an API key at [https://itzuli.vicomtech.org/en/api/](https://itzuli.vicomtech.org/en/api/)
2. Set the `ITZULI_API_KEY` environment variable

Runs over stdio transport.

```bash
ITZULI_API_KEY=your-key uv run python -m itzuli_stanza_mcp.itzuli_mcp_server
```

### Tools

- **translate** — Translate text to or from Basque using the official Itzuli API. Supported pairs: eu<->es, eu<->en, eu<->fr.
- **get_quota** — Check current API usage quota.
- **send_feedback** — Submit a correction or evaluation for a previous translation.

### Combined Workflow

For comprehensive Basque language processing:

1. Use Itzuli to translate text to/from Basque
2. Use Stanza to analyze the Basque text for detailed grammatical insights
3. Combine results for enriched linguistic understanding
