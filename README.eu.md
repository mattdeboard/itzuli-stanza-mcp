# itzuli-stanza-mcp

[🇺🇸 English](README.md) | [🔴⚪🟢 Euskera](README.eu.md)

Euskal hizkuntzaren prozesamendu tresna-sorta bat da, [Itzuli](https://www.euskadi.eus/itzuli/) APIaren itzulpen gaitasunak eta [Stanza](https://stanfordnlp.github.io/stanza/)ren bidezko analisi morfologiko zehatza konbinatzen dituena. Sistemak itzulpen zerbitzuak eta analisi linguistikoa eskaintzen ditu MCP zerbitzarietan paketatuta.

## Ikuspegi orokorra

Proiektu honek bi zerbitzu osagarri eskaintzen ditu:

1. **Itzuli Itzulpen Zerbitzua** — Euskal Gobernuaren itzulpen API ofiziala euskera ↔ gaztelania/ingelesa/frantsesera itzulpen kalitatetsuetarako
2. **Stanza Analisi Morfologikoa** — Stanford NLP tresna-sorta euskal testuaren banaketa gramatikala, lematizazioa, POS etiketatua eta ezaugarri linguistikoak eskaintzen dituena

Zerbitzuak independenteki edo batera erabil daitezke euskal hizkuntzaren prozesamendu osatuetarako.

## Proiektuaren egitura

Egitura osoaren xehetasunetarako ikus [ARCHITECTURE.eu.md](./ARCHITECTURE.eu.md).

```code
itzuli_stanza_mcp/
  itzuli_mcp_server.py   # MCP zerbitzaria itzulpena eta analisi morfologikoarekin
  services.py            # Itzuli eta Stanza koordinatzen dituen zerbitzu geruza
  nlp.py                 # Stanza pipelinearen konfigurazioa eta testu prozesamendu
```

## Itzuli Itzulpen MCP Zerbitzaria

Model Context Protocol bidez itzulpena eta analisi morfologikoa eskaintzen ditu. Itzulpen bakoitzak automatikoki Stanford-en [Stanza pipeline neuronal](https://stanfordnlp.github.io/stanza/neural_pipeline.html)a erabiliz euskal testuaren analisi gramatiko zehatza barne hartzen du.

### API Gakoaren Konfigurazioa

Itzuli itzulpen zerbitzua erabiltzeko, API gako bat behar duzu:

1. API gako bat eskatu [https://itzuli.vicomtech.org/en/api/](https://itzuli.vicomtech.org/en/api/) helbidean
2. `ITZULI_API_KEY` ingurumen aldagaia ezarri

stdio garraio bidez funtzionatzen du.

```bash
ITZULI_API_KEY=zure-gakoa uv run python -m itzuli_stanza_mcp.itzuli_mcp_server
```

### Tresnak

- **translate** — Itzuli API ofiziala erabiliz euskerara edo euskeratik testua itzuli. Onartutako bikoteak: eu<->es, eu<->en, eu<->fr. Aukerako `output_language` parametroak 'en', 'eu', 'es', 'fr' onartzen ditu taula goiburuen lokalizaziorako.
- **get_quota** — Uneko API erabilera kuota egiaztatu.
- **send_feedback** — Aurreko itzulpen baterako zuzentzaile edo ebaluazioa bidali.

### AI Laguntzaileekin Erabilera

AI laguntzaileekin lan egitean MCP zerbitzari honetara sarbidea dutenean, irteera hizkuntzaren hobespenak zaindu ahal dituzu modu askotan:

**Itzulpen gonbiteekin irteera hizkuntzaren hobespena erabiliz:**

```text
@en@eu Hello, mesedez itzuli hau euskerara eta erakutsi analisia euskeraz
```

**Euskal irteerarako argibide zuzena:**

```text
Itzuli "Hello" ingelesetik euskerara output_language="eu" erabiliz analisi taulak euskal goiburuak erakuts ditzan
```

**Saiorako hizkuntza hobespena ezarriz:**

```text
Elkarrizketa honetako itzulpen guztietarako, mesedez erabili output_language="eu" analisi morfologikoa euskeraz erakusteko
```

**Tresna erabilera zuzenaren zehaztapena:**

```python
translate(text="Kaixo", source_language="eu", target_language="en", output_language="eu")
```

`output_language` parametroak analisi morfologikoaren taula goiburu eta etiketen hizkuntza kontrolatzen du, ez itzulpenaren norabidea.

### Irteeraren adibidea

Analisi morfologiko automatikoa duen itzulpena:

```text
Jatorria: No conozco las canciones vascas (Spanish)
Itzulpena: Ez ditut ezagutzen euskal abestiak (Basque)

Analisi Morfologikoa:
| Hitza     | Lema      | Ezaugarriak                                             |
| --------- | --------- | ------------------------------------------------------- |
| Ez        | (ez)      | ezeztapena                                              |
| ditut     | (ukan)    | adierazpen modua, objektu plurala, subjektu singularra, |
|           |           | 3. pertsona obj (hura/haiek), 1. pertsona subj (nik),   |
|           |           | aditz jokatua                                           |
| ezagutzen | (ezagutu) | ohikoa/jarraian                                         |
| euskal    | (euskal)  | konbinazio aurrizkia                                    |
| abestiak  | (abesti)  | absolutiboa (nor), mugatu (-a/-ak), plurala             |
```
