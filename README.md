# stanza-server

A Flask web server that provides Basque language morphological analysis using [Stanza](https://stanfordnlp.github.io/stanza/). It tokenizes Basque text and returns per-word glossing data (lemma, grammatical features) as JSON.

Intended for use as a backend for the [itzuli-mcp](https://github.com/mattdeboard/itzuli-mcp) MCP server.

## Usage

```bash
uv run python main.py
```

The server runs on port 5001.

### `POST /stanza`

```bash
curl -X POST http://localhost:5001/stanza \
  -H "Content-Type: application/json" \
  -d '{"text": "Ez ditut ezagutzen euskal abestiak"}'
```

Response:

```json
[
  {"word": "Ez", "lemma": "(ez)", "feats": "negation"},
  {"word": "ditut", "lemma": "(ukan)", "feats": "indicative mood, plural obj, singular sub, 3per obj (it/them), 1per sub (I), conjugated"},
  {"word": "ezagutzen", "lemma": "(ezagutu)", "feats": "habitual/ongoing"},
  {"word": "euskal", "lemma": "(euskal)", "feats": "combining prefix"},
  {"word": "abestiak", "lemma": "(abesti)", "feats": "absolutive (sub/obj), definite (the), plural"}
]
```
