# BibleMate AI Data

Essential Bible data for [BibleMate Web](https://github.com/eliranwong/biblemateweb) and [BibleMate Agentic Workspace](https://github.com/eliranwong/biblemate-agentic-workspace) (part of [BibleMate AI](https://github.com/eliranwong/biblemate)).

Web Demo: https://app.biblemate.ai

---

## Built For

- **BibleMate Web** (Web GUI / HTTP Server / API Server): https://github.com/eliranwong/biblemateweb
- **BibleMate Agentic Workspace**: https://github.com/eliranwong/biblemate-agentic-workspace
- **BibleMate CLI** (CLI version / MCP server): https://github.com/eliranwong/biblematecli

## Requirement

- Python `>= 3.10`
- `git` command line tool (only required if downloading Bible audio files)

## Installation

1. Install or upgrade the `biblematedata` package:

```bash
pip install --upgrade --no-cache-dir biblematedata
```

2. Download and set up the data into `~/biblemate`:

- **Full setup** (recommended for **BibleMate Web**):

```bash
biblematedata
```

By default, this installs:
- **Databases** into `~/biblemate/data`
- **Podcast files** into `~/biblemate/data/podcast`
- **Custom data folders** in `~/biblemate/data_custom/` (`lexicons`, `commentaries`, `audio`, `bibles`, `books`, `clauses`)
- **BibleMate agentic workspace** into `~/biblemate`
- **Default Bible audio** (`NET` American accent, `OHGB` slow, `BHS5`, and `OGNT`) into `~/biblemate/data/audio/bibles/<module>/default`, followed by an interactive prompt to download additional Bible audio

- **Databases & workspace only** (skip podcast and Bible audio — recommended for **BibleMate Agentic Workspace** users):

```bash
biblematedata --no-podcast --no-audio
```

### Downloading Additional Bible Audio

During `biblematedata` (without `--no-audio`), an interactive menu appears after the default audio modules (`NET`, `OHGB`, `BHS5`, `OGNT`) so you can select and download additional supported Bible audio modules (or replace existing ones) until you cancel.

To download additional Bible audio at any time without re-running the full setup, run:

```bash
biblematedata --audio-only
```

### Available Options

- `--no-podcast` — Skip downloading podcast files from [biblematedata-podcast](https://github.com/eliranwong/biblematedata-podcast).
- `--no-audio` — Skip downloading Bible audio files.
- `--podcast-only` — Only download podcast files from [biblematedata-podcast](https://github.com/eliranwong/biblematedata-podcast).
- `--audio-only` — Only download Bible audio files.
- `--workspace-only` — Only download and unpack the BibleMate agentic workspace into `~/biblemate`.

## Troubleshoot

If there are errors due to connectivity issues, run `biblematedata` (with the same flags) again—already downloaded files will be skipped automatically.

## Related Data Repositories

- BibleMate Data - Podcast: https://github.com/eliranwong/biblematedata-podcast
- BibleMate Data - Names: https://github.com/eliranwong/biblematedata-names
- BibleMate Data - Lexicon Mapping (HALOT, CHALOT, BDBE, BDAG, LSJ): https://github.com/eliranwong/biblematedata-mapping-HALOT-CHALOT-BDBE-BDAG-LSJ
- BibleMate Data - Tagged Bibles: https://github.com/eliranwong/biblematedata-tagged-bibles
