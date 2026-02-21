# Itzuli + Stanza NLP Integrazioa

[🇺🇸 English](README.md) | [🔴⚪🟢 Euskera](README.eu.md)

Hau euskal NLP sistema bat duen monorepo bat da, itzulpen eta analisi morfologikoko gaitasunak web-oinarritutako lerrokatze bistaratzaile interfaze batekin integratzen dituena.

## Demoa

![Lerrokatze Bistaratzaile Demoa](resources/demo.gif)

## Proiektuaren Egitura

```text
itzuli-stanza-mcp/
├── backend/           # Python NLP backend-a MCP zerbitzariarekin
└── frontend/          # TypeScript + React lerrokatze bistaratzailea
```

## Osagaiak

### Backend-a

Python oinarritutako NLP prozesatze zerbitzaria:

- Stanza integrazioa analisi morfologikorako
- Itzulpen lerrokatze algoritmoak
- MCP (Model Context Protocol) zerbitzaria Claude integraziorako

### Frontend-a

React oinarritutako bistaratzaile interfazea:

- Lerrokatze bistaratzaile interaktiboa zintak animatuez
- Geruza anitzeko lerrokatze laguntza (lexikala, morfologikoa, sintaktikoa)
- Token nabarmentze eta ainguratze funtzionaltasuna
- Denbera errealeko datu eskuratzea backend API-tik

## Dokumentazioa

Dokumentazio zehatzerako, ikus:

- **[Backend README](backend/README.eu.md)** - Python backend dokumentazioa
- **[Arkitektura Dokumentazioa](backend/ARCHITECTURE.eu.md)** - Sistemaren arkitektura zehatza
