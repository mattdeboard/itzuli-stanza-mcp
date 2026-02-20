# Architecture Documentation

[🇺🇸 English](ARCHITECTURE.md) | [🔴⚪🟢 Euskera](ARCHITECTURE.eu.md)

This document provides a comprehensive overview of the itzuli-stanza-mcp project architecture.

## Project Overview

A Basque language processing system that combines translation capabilities from the Itzuli API with detailed morphological analysis via Stanford's Stanza library. The system provides an MCP (Model Context Protocol) server for AI assistant integration, delivering both translation and linguistic analysis in a single unified interface.

## Project Structure

```code
itzuli_stanza_mcp/
├── itzuli_mcp_server.py   # MCP server providing translation with morphological analysis
├── services.py            # MCP-specific glue layer
├── workflow.py            # Core translation+analysis workflow (reusable)
├── formatters.py          # Output formatting (markdown, JSON, dict list)
├── nlp.py                 # Stanza pipeline configuration and text processing logic
├── i18n.py                # Internationalization data for localized output
└── __init__.py
tests/
├── test_itzuli_mcp_server.py
├── test_workflow.py       # Tests for core workflow functionality
├── test_formatters.py     # Tests for output formatting
└── __init__.py
pyproject.toml             # Project dependencies and configuration
README.md                  # User documentation
CLAUDE.md                  # Development guidelines
```

## Core Components

### 1. Translation Service (`itzuli_mcp_server.py`)

- **Technology**: MCP (Model Context Protocol) server with FastMCP
- **Purpose**: Combined translation and morphological analysis for AI assistants
- **Transport**: stdio
- **Authentication**: Requires `ITZULI_API_KEY` environment variable
- **Dependencies**: `services.py` for coordinated processing

### 2. Core Workflow Module (`workflow.py`)

- **Purpose**: Reusable core business logic for translation + analysis
- **Pattern**: Pure functions returning structured data
- **Key Function**: `process_translation_with_analysis()` - coordinates Itzuli + Stanza
- **Design**: Framework-agnostic, can be used outside MCP context
- **Dependencies**: Itzuli API, Stanza pipeline, NLP processing

### 3. Output Formatting Module (`formatters.py`)

- **Purpose**: Multiple output format support for translation results
- **Functions**:
  - `format_as_markdown_table()` - Formatted table with 100-column wrapping
  - `format_as_json()` - JSON output with full data
  - `format_as_dict_list()` - Python dictionaries for programmatic use
- **Design**: Pure functions accepting structured workflow results

### 4. Service Coordination Layer (`services.py`)

- **Purpose**: MCP-specific glue layer combining workflow + formatting
- **Pattern**: Thin wrapper functions for MCP server
- **Functions**: `translate_with_analysis`, `get_quota`, `send_feedback`
- **Design**: Maintains backward compatibility for existing MCP tools

### 5. NLP Processing Module (`nlp.py`)

- **Technology**: Stanford Stanza library
- **Purpose**: Basque language processing and feature extraction
- **Pipeline**: tokenize, POS tagging, lemmatization
- **Features**: Friendly feature mapping for linguistic annotations

### 6. Internationalization Module (`i18n.py`)

- **Purpose**: Localized labels and language names
- **Languages**: English, Basque, Spanish, French
- **Data**: Output labels, language names, friendly feature descriptions
- **Usage**: Supports localized analysis output in multiple languages

## System Architecture

```code
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  MCP Client     │───▶│  MCP Server      │───▶│  Services Layer  │
│  (AI Assistant) │    │    (stdio)       │    │   (MCP glue)     │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                                                        │
                                                        ▼
                                                ┌──────────────────┐
                                                │ Workflow Module  │
                                                │ (Core Logic)     │
                                                └──────────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              ▼                         ▼                         ▼
                   ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
                   │  Itzuli API      │       │ Stanza Pipeline  │       │ Formatters       │
                   │ (Translation)    │       │   (Analysis)     │       │ (Multiple Types) │
                   └──────────────────┘       └──────────────────┘       └──────────────────┘
```

## Data Flow

### Translation Flow

1. MCP client invokes translation tool
2. MCP server validates language pair (must include Basque)
3. Services layer calls workflow module with translation parameters
4. Workflow module calls Itzuli API for translation
5. Workflow module determines Basque text (source or translated)
6. Workflow module processes Basque text through Stanza pipeline
7. Workflow module returns structured TranslationResult data
8. Services layer calls appropriate formatter (markdown table for MCP)
9. Formatted result returned to MCP client

### Alternative Usage (Direct Workflow)

For non-MCP applications:

1. Application calls `process_translation_with_analysis()` directly
2. Workflow returns structured TranslationResult
3. Application chooses formatter: markdown, JSON, or dict list
4. Formatted output used as needed

## External Integrations

### Itzuli API

- **Purpose**: Basque translation service
- **Authentication**: API key via environment variable
- **Supported Languages**: Basque ↔ Spanish, English, French
- **Endpoints Used**: Translation, quota checking, feedback submission

### Stanford Stanza

- **Purpose**: Basque morphological analysis
- **Model**: Pre-trained Basque language model
- **Download Strategy**: Reuse existing resources
- **Processors**: tokenize, pos, lemma

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

## Deployment

### MCP Server

```bash
ITZULI_API_KEY=your-key uv run python -m itzuli_stanza_mcp.itzuli_mcp_server
```

## Future Considerations

- Consider adding batch processing for multiple texts
- Potential caching layer for frequently analyzed text
- Additional language pairs if Itzuli API expands support
- Additional output formatters (XML, CSV, etc.) can be easily added
- The workflow module enables building separate tools for translation-only or analysis-only use cases

## Glossary

- **MCP**: Model Context Protocol - standard for AI assistant tool integration
- **Stanza**: Stanford NLP library for multilingual text analysis
- **Itzuli**: Basque government's official translation API
- **Morphological Analysis**: Breaking down words into their grammatical components
- **Lemmatization**: Finding the base/dictionary form of words
