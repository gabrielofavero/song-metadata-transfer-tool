# Song Metadata Transfer Tool

A Streamlit application for copying and adapting song metadata between audio files.  
Supports **MP3 and FLAC**, single-file transfers, and batch processing with automatic file matching.

This tool is ideal if you’ve re-encoded your library or downloaded cleaner audio files but want to **preserve the original tags** — title, artist, album, composer, etc.

---

## Features

- Copy metadata from one track to another
- Batch mode for multiple files
- Automatic filename-based matching
- Optionally remove track numbers
- Album name override (single or batch)
- Optional deletion of source files after transfer
- Direct download (single) or ZIP archive (batch)

Supported formats:

- MP3 (`EasyID3`)
- FLAC (`mutagen.flac.FLAC`)

---

## Requirements

Python **3.8+**

Dependencies (installed automatically):

- `streamlit`
- `mutagen`

---

## Installation

Clone the repository:

```bash
git clone https://github.com/gabrielofavero/song-metadata-transfer-tool
cd song-metadata-transfer-tool
```

Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# or
.\.venv\Scripts\activate    # Windows
```

Install dependencies:

```bash
pip install -e .
```

Or install directly from pyproject.toml:

```bash
pip install -r requirements.txt
```