# itzuli-stanza-mcp

[🇺🇸 English](README.md) | [🔴⚪🟢 Euskera](README.eu.md)

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
  itzuli_mcp_server.py   # MCP server providing translation with morphological analysis
  services.py            # Service layer coordinating Itzuli and Stanza
  nlp.py                 # Stanza pipeline and text processing
```

## Itzuli Translation MCP Server

Provides translation and morphological analysis through the Model Context Protocol. Each translation automatically includes detailed grammatical analysis of the Basque text using Stanford's [Stanza neural pipeline](https://stanfordnlp.github.io/stanza/neural_pipeline.html).

### API Key Setup

To use the Itzuli translation service, you need an API key:

1. Apply for an API key at [https://itzuli.vicomtech.org/en/api/](https://itzuli.vicomtech.org/en/api/)
2. Set the `ITZULI_API_KEY` environment variable

Runs over stdio transport.

```bash
ITZULI_API_KEY=your-key uv run python -m itzuli_stanza_mcp.itzuli_mcp_server
```

### Tools

- **translate** — Translate text to or from Basque using the official Itzuli API. Supported pairs: eu<->es, eu<->en, eu<->fr. Optional `output_language` parameter supports 'en', 'eu', 'es', 'fr' for localized table headers.
- **get_quota** — Check current API usage quota.
- **send_feedback** — Submit a correction or evaluation for a previous translation.

### Usage with AI Assistants

When working with AI assistants that have access to this MCP server, you can specify output language preferences in several ways:

**Using translation prompts with output language preference:**

```text
@eu@en Hello, please translate this to Basque and show analysis in Basque
```

**Explicit instruction for Basque output:**

```text
Translate "Hello" from English to Basque using output_language="eu" so the analysis table uses Basque headers
```

**Setting language preference for the session:**

```text
For all translations in this conversation, please use output_language="eu" to show morphological analysis in Basque
```

**Direct tool usage specification:**

```python
translate(text="Hello", source_language="en", target_language="eu", output_language="eu")
```

The `output_language` parameter controls the language of table headers and labels in the morphological analysis, not the translation direction.

### Example Output

Translation with automatic morphological analysis:

```text
Source: I don't know Basque songs (English)
Translation: Ez ditut ezagutzen euskal abestiak (Basque)

Morphological Analysis:
| Word      | Lemma     | Features                                                 |
| --------- | --------- | -------------------------------------------------------- |
| Ez        | (ez)      | negation                                                 |
| ditut     | (ukan)    | indicative mood, plural obj, singular sub,               |
|           |           | 3rd person obj (it/them), 1st person sub (I), conjugated |
| ezagutzen | (ezagutu) | habitual/ongoing                                         |
| euskal    | (euskal)  | combining prefix                                         |
| abestiak  | (abesti)  | absolutive (sub/obj), definite (the), plural             |
```
