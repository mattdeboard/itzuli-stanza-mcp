# Architecture Documentation

[🇺🇸 English](ARCHITECTURE.md) | [🔴⚪🟢 Euskera](ARCHITECTURE.eu.md)

This document provides a comprehensive overview of the itzuli-nlp project architecture.

## Project Overview

A modular Basque language processing system that combines translation capabilities from the Itzuli API with detailed morphological analysis via Stanford's Stanza library. The system provides reusable NLP components and an MCP (Model Context Protocol) server for AI assistant integration.

## Project Structure

```code
itzuli_nlp/                # Core reusable NLP library
├── workflow.py            # Core translation+analysis workflow
├── nlp.py                 # Stanza pipeline configuration and text processing
├── formatters.py          # Output formatting (markdown, JSON, dict list)
├── types.py               # Shared data types (AnalysisRow, TranslationResult)
├── i18n.py                # Internationalization data for localized output
└── __init__.py

mcp_server/                # MCP-specific code
├── server.py              # MCP tool definitions and endpoints
├── services.py            # MCP glue layer (thin wrapper)
└── __init__.py

scripts/                   # Utility scripts
├── dual_analysis.py       # Analyzes both source & translation text
├── playground/            # Development/testing scripts
│   ├── itzuli_playground.py
│   └── stanza_playground.py
└── __init__.py

tests/                     # Test suite
├── test_itzuli_mcp_server.py # MCP server tests
├── test_workflow.py       # Core workflow tests
├── test_formatters.py     # Output formatting tests
├── test_nlp.py            # NLP processing tests
└── __init__.py

pyproject.toml             # Project dependencies and configuration
README.md                  # User documentation
CLAUDE.md                  # Development guidelines
```

## Core Components

### 1. Core NLP Library (`itzuli_nlp/`)

**Workflow Module (`workflow.py`)**

- **Purpose**: Reusable core business logic for translation + analysis
- **Key Function**: `process_translation_with_analysis()` - coordinates Itzuli + Stanza
- **Design**: Framework-agnostic, returns structured `TranslationResult` data
- **Dependencies**: Itzuli API, Stanza pipeline, NLP processing

**NLP Processing Module (`nlp.py`)**

- **Technology**: Stanford Stanza library with multi-language support
- **Functions**: `create_pipeline(language)`, `process_raw_analysis()`
- **Pipeline**: tokenize, POS tagging, lemmatization
- **Features**: Raw Stanza output as typed `AnalysisRow` objects

**Output Formatting Module (`formatters.py`)**

- **Purpose**: Multiple output format support for translation results
- **Functions**:
  - `format_as_markdown_table()` - Formatted table with 100-column wrapping
  - `format_as_json()` - JSON output with full data
  - `format_as_dict_list()` - Python dictionaries for programmatic use
- **Design**: Pure functions with friendly feature mapping

**Types Module (`types.py`)**

- **Purpose**: Shared data structures to avoid circular imports
- **Types**: `AnalysisRow`, `TranslationResult`, `LanguageCode`
- **Design**: Simple dataclasses for type safety

**Internationalization Module (`i18n.py`)**

- **Purpose**: Localized labels and language names
- **Languages**: English, Basque, Spanish, French
- **Data**: Output labels, language names, friendly feature descriptions

### 2. MCP Server (`mcp_server/`)

**Server Module (`server.py`)**

- **Technology**: MCP (Model Context Protocol) server with FastMCP
- **Purpose**: AI assistant integration with translation and analysis tools
- **Transport**: stdio
- **Authentication**: Requires `ITZULI_API_KEY` environment variable

**Service Coordination Layer (`services.py`)**

- **Purpose**: MCP-specific glue layer combining core workflow + formatting
- **Pattern**: Thin wrapper functions for MCP server
- **Functions**: `translate_with_analysis`, `get_quota`, `send_feedback`
- **Design**: Maintains backward compatibility for existing MCP tools

### 3. Utility Scripts (`scripts/`)

**Dual Analysis Script (`dual_analysis.py`)**

- **Purpose**: Analyze both source and translated text using separate pipelines
- **Usage**: `python -m scripts.dual_analysis "text" --source eu --target en`
- **Features**: Multi-language Stanza analysis, JSON/table output
- **Design**: Standalone utility for advanced NLP analysis

## System Architecture

```code
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  MCP Client     │───▶│  MCP Server      │───▶│ mcp_server/      │
│  (AI Assistant) │    │    (stdio)       │    │ services.py      │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐                           ┌──────────────────┐
│ Direct Usage    │──────────────────────────▶│ itzuli_nlp/      │
│ (scripts,apps)  │                           │ workflow.py      │
└─────────────────┘                           └──────────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              ▼                         ▼                         ▼
                   ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
                   │  Itzuli API      │       │ itzuli_nlp/      │       │ itzuli_nlp/      │
                   │ (Translation)    │       │ nlp.py           │       │ formatters.py    │
                   └──────────────────┘       └──────────────────┘       └──────────────────┘
```

## Data Flow

### MCP Translation Flow

1. MCP client invokes translation tool
2. `mcp_server/server.py` validates language pair (must include Basque)
3. `mcp_server/services.py` calls `itzuli_nlp/workflow.py` with parameters
4. Workflow module calls Itzuli API for translation
5. Workflow module determines Basque text (source or translated)
6. Workflow module processes Basque text through Stanza pipeline (single language)
7. Workflow module returns structured `TranslationResult` data
8. Services layer calls `format_as_markdown_table()` for MCP output
9. Formatted result returned to MCP client

### Direct Usage (Reusable Components)

For applications using the NLP library directly:

1. Application imports `itzuli_nlp.workflow` or `itzuli_nlp.nlp` directly
2. Calls core functions like `process_translation_with_analysis()`
3. Receives structured data (`TranslationResult`, `List[AnalysisRow]`)
4. Application chooses formatter: markdown, JSON, or dict list
5. Formatted output used as needed

### Dual Analysis Flow (scripts/dual_analysis.py)

1. Script calls Itzuli API for translation
2. Creates separate Stanza pipelines for source and target languages
3. Processes both source and translated text through appropriate pipelines
4. Returns separate `List[AnalysisRow]` for each language
5. Formats output showing morphological analysis for both texts

## External Integrations

### Itzuli API

- **Purpose**: Basque translation service
- **Authentication**: API key via environment variable
- **Supported Languages**: Basque ↔ Spanish, English, French
- **Endpoints Used**: Translation, quota checking, feedback submission

### Stanford Stanza

- **Purpose**: Multi-language morphological analysis
- **Models**: Pre-trained language models (Basque, English, Spanish, French)
- **Download Strategy**: Reuse existing resources
- **Processors**: tokenize, pos, lemma (+ mwt for some languages)
- **Usage**: Separate pipelines created per language for accurate analysis

## Security Considerations

- API key stored in environment variables (not hardcoded)
- Input validation for supported language pairs
- Error handling prevents information leakage
- MCP server runs over stdio (no network exposure)

## Development Environment

### Dependencies

- **Core**: Stanza, Itzuli, MCP
- **Development**: pytest, ruff, anyio
- **Python Version**: ≥3.10

### Testing

- Test suite in `tests/` directory
- Focus on MCP server functionality
- Run with: `pytest`

### Code Quality

- Linting with ruff
- Type hints where applicable
- Logging configured via environment variables

## Usage

### MCP Server

```bash
ITZULI_API_KEY=your-key uv run python -m mcp_server.server
```

### Dual Analysis Script

```bash
uv run python -m scripts.dual_analysis "Kaixo mundua" --source eu --target en --format table
```

## Future Considerations

- Consider adding batch processing for multiple texts
- Potential caching layer for frequently analyzed text
- Additional language pairs if Itzuli API expands support
- Additional output formatters (XML, CSV, etc.) can be easily added
- The modular structure enables building separate tools for translation-only or analysis-only use cases
- Consider expanding scripts/ directory with additional utilities
- Multi-language analysis capabilities could be extended beyond current supported languages

## Glossary

- **MCP**: Model Context Protocol - standard for AI assistant tool integration
- **Stanza**: Stanford NLP library for multilingual text analysis
- **Itzuli**: Basque government's official translation API
- **Morphological Analysis**: Breaking down words into their grammatical components
- **Lemmatization**: Finding the base/dictionary form of words
