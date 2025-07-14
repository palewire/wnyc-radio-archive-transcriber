# WNYC Radio Archive Transcriber

Scrape and transcribe thousands of audio files for free using Python, OpenAI's Whisper, and GitHub Actions.

This repository demonstrates how to:
1. **Scrape** thousands of MP3 files from the [NYC Municipal Archive's WNYC radio collection](https://nycrecords.access.preservica.com/uncategorized/SO_4574c0f5-03e8-4f9b-a0c6-d1c8ff23759b/?pg=1)
2. **Transcribe** them automatically using OpenAI's Whisper speech-to-text model
3. **Scale** the process using GitHub Actions matrix operations to process files in parallel
4. **Store** results as searchable text files in your repository

It works because:

- **Cost**: $0 using free tools and GitHub Actions
- **Quality**: Whisper provides state-of-the-art transcription
- **Scale**: GitHub Actions can process hundreds of files in parallel
- **Simplicity**: Fully automated once set up

### Directory Structure

```
wnyc-radio-archive-transcriber/
├── pipeline/                    # Core processing modules
│   ├── settings.py             # Configuration and paths
│   ├── utils.py                # Shared utility functions
│   ├── scrape.py               # Web scraping logic
│   ├── transcribe.py           # Audio transcription
│   ├── count.py                # Progress tracking
│   └── untranscribed.py        # File management
├── data/                       # Data storage
│   ├── input/                  # Scraped data
│   │   ├── html/              # Raw HTML files
│   │   │   ├── lists/         # List page HTML
│   │   │   └── details/       # Detail page HTML
│   │   └── json/              # Structured metadata
│   └── output/                # Transcription results
├── .github/workflows/          # Automation
│   ├── scrape.yaml            # Metadata collection
│   └── transcribe.yaml        # Parallel transcription
├── README.md                  # Quick start guide
└── pyproject.toml           # Dependencies and config
```

## Usage

Clone this repository.

```bash
git clone https://github.com/palewire/wnyc-radio-archive-transcriber.git
cd wnyc-radio-archive-transcriber
```

Install dependencies.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

Check for untranscribed files.

```bash
uv run python -m pipeline.count
```

Scrape new files from the WNYC archive.

```bash
uv run python -m pipeline.scrape
```

List untranscribed files.

```bash
uv run python -m pipeline.untranscribed -l 1
```

```bash
uv run python -m pipeline.scrape
```

List untranscribed files.

```bash
uv run python -m pipeline.untranscribed -l 1
```

Transcribe a single file.

```bash
uv run python -m pipeline.transcribe -f "your-file-id-here"
```

### How the matrix strategy mass transcribes files

The [transcription workflow](https://github.com/palewire/wnyc-radio-archive-transcriber/.github/workflows/transcribe.yaml) uses GitHub Actions' matrix strategy to process multiple files simultaneously:

```yaml
strategy:
  fail-fast: false
  matrix:
    file: ${{ fromJson(needs.seed.outputs.file-list) }}
```

This creates a separate job for each file, allowing GitHub to process hundreds of files in parallel across multiple runners.
