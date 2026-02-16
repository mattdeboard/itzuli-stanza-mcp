# Architecture Documentation

This document provides a comprehensive overview of the itzuli-stanza-mcp project architecture.

## Project Overview

A Basque language processing system that combines translation capabilities from the Itzuli API with detailed morphological analysis via Stanford's Stanza library. The system provides an MCP (Model Context Protocol) server for AI assistant integration, delivering both translation and linguistic analysis in a single unified interface.

## Project Structure

```code
itzuli_stanza_mcp/
├── itzuli_mcp_server.py   # MCP server providing translation with morphological analysis
├── services.py            # Service layer coordinating Itzuli and Stanza
├── nlp.py                 # Stanza pipeline configuration and text processing logic
└── __init__.py
tests/
├── test_itzuli_mcp_server.py
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

### 2. Service Coordination Layer (`services.py`)

- **Purpose**: Functional layer coordinating Itzuli and Stanza services
- **Pattern**: Pure functions with lazy-loaded Stanza pipeline caching
- **Functions**: `translate_with_analysis`, `get_quota`, `send_feedback`
- **Design**: No global state, clean separation of concerns

### 3. NLP Processing Module (`nlp.py`)

- **Technology**: Stanford Stanza library
- **Purpose**: Basque language processing and feature extraction
- **Pipeline**: tokenize, POS tagging, lemmatization
- **Features**: Friendly feature mapping for linguistic annotations

## System Architecture

```code
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  MCP Client     │───▶│  MCP Server      │───▶│  Services Layer  │
│  (AI Assistant) │    │    (stdio)       │    │ (coordination)   │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              ▼                         ▼                         ▼
                   ┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
                   │  Itzuli API      │       │ Stanza Pipeline  │       │ Output Formatter │
                   │ (Translation)    │       │   (Analysis)     │       │ (Markdown Table) │
                   └──────────────────┘       └──────────────────┘       └──────────────────┘
```

## Data Flow

### Translation Flow

1. MCP client invokes translation tool
2. Server validates language pair (must include Basque)
3. Services layer calls Itzuli API for translation
4. Services layer determines Basque text (source or translated)
5. Services layer processes Basque text through Stanza pipeline
6. Services layer formats combined output with source, translation, and analysis table
7. Formatted result returned to MCP client

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
- Separate tools for translation-only vs analysis-only workflows

## Glossary

- **MCP**: Model Context Protocol - standard for AI assistant tool integration
- **Stanza**: Stanford NLP library for multilingual text analysis
- **Itzuli**: Basque government's official translation API
- **Morphological Analysis**: Breaking down words into their grammatical components
- **Lemmatization**: Finding the base/dictionary form of words
