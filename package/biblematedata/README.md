# BibleMate AI Data

Essential Bible data for [BibleMate Web](https://github.com/eliranwong/biblemateweb) and [BibleMate Agentic Workspace](https://github.com/eliranwong/biblemate-agentic-workspace) (part of [BibleMate AI](https://github.com/eliranwong/biblemate)).

Web Demo: https://web.biblemate.ai

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
pip install -U biblematedata
```

2. Download and set up the data into `~/biblemate/data`:

- **Full setup** (databases, podcast files, and Bible audio — recommended for **BibleMate Web**):

```bash
biblematedata
```

- **Databases only** (skip podcast and Bible audio — recommended for **BibleMate Agentic Workspace** users):

```bash
biblematedata --no-podcast --no-audio
```

### Available Options

- `--no-podcast` — Skip downloading podcast files from [biblematedata-podcast](https://github.com/eliranwong/biblematedata-podcast).
- `--no-audio` — Skip downloading Bible audio files.

## Troubleshoot

If there are errors due to connectivity issues, run `biblematedata` (with the same flags) again—already downloaded files will be skipped automatically.

## Related Data Repositories

- BibleMate Data - Podcast: https://github.com/eliranwong/biblematedata-podcast
- BibleMate Data - Names: https://github.com/eliranwong/biblematedata-names
- BibleMate Data - Lexicon Mapping (HALOT, CHALOT, BDBE, BDAG, LSJ): https://github.com/eliranwong/biblematedata-mapping-HALOT-CHALOT-BDBE-BDAG-LSJ
- BibleMate Data - Tagged Bibles: https://github.com/eliranwong/biblematedata-tagged-bibles
