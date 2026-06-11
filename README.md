# Synthetic Transaction Narration Generator (India)

A production-grade Python pipeline designed to generate highly realistic Indian bank transaction narrations (e.g., UPI, IMPS, NEFT, RTGS, POS) using Gemini Models (such as Gemma/Gemini) via the Google GenAI SDK. It features strict **one-narration-per-call** generation, real-time verification and validation, deduplication, and crash-safe resume capabilities.

---

## Key Features

- **High-Fidelity Generation**: Synthesizes realistic bank statement lines (truncations, mixed case, transaction IDs, specific UPI handles, dates, and noise/transaction code tokens).
- **Target Distribution**: Enforces a progressive distribution ratio (default: **90% P2P** and **10% Merchant** transactions).
- **Zero-Batching Constraint**: Adheres to the requirement of exactly one narration generated per API call (no batching or prompt arrays).
- **Validation Pipeline**: Standardizes, sanitizes, and runs structural validation on each output. Rejects non-conforming or generic responses.
- **Deduplication**: Automatically hashes normalized narrations to ensure no duplicates exist across the generated dataset.
- **Crash-Safe Resume**: Persists metrics and data incrementally. Rebuilds the memory state from `output.jsonl` upon startup, allowing the pipeline to resume seamlessly.

---

## Directory Structure

The project follows a standard modern `src/` layout for Python packaging:

```text
.
├── .gitignore                      # Configured git ignore patterns
├── README.md                       # Documentation
├── pyproject.toml                  # Standard package definition & dependencies
├── requirements.txt                # Legacy dependencies list
├── transactions.csv                # Sample input dataset containing real narrations
├── main.py                         # Root-level entrypoint script
└── src/
    └── synthetic_txn_generator/    # Main application package
        ├── __init__.py
        ├── checkpoint.py           # Generation metrics checkpoints
        ├── exporter.py             # Append-only JSONL exporter
        ├── generator.py            # Narration generator engine
        ├── labeler.py              # Payee and counterparty extraction labeler
        ├── llm_client.py           # Throttled, concurrent LLM API client wrapper
        ├── main.py                 # Core CLI application entrypoint logic
        ├── prompt_builder.py       # Few-shot prompt construct builder
        └── validator.py            # Narration structure and content validator
```

---

## Setup & Installation

### Prerequisite: API Key Configuration

Obtain a Gemini API key and set the environment variable:

```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your_api_key_here"

# Linux / macOS
export GEMINI_API_KEY="your_api_key_here"
```

### Option A: Standard Run (No-Install Bootstrapping)

Set up a virtual environment, install requirements, and run directly using the root entrypoint:

```bash
# 1. Setup virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run directly
python main.py --mode generate --input transactions.csv --total 10000
```

### Option B: Package Installation (CLI Command Wrapper)

You can install the codebase as an editable package so the CLI command wrapper `synthetic-txns` is available globally in your environment:

```bash
# 1. Install package in editable mode
pip install -e .

# 2. Execute using command wrapper
synthetic-txns --mode generate --input transactions.csv --total 10000
```

---

## Command Line Arguments

The tool provides two modes: `generate` and `label`.

```text
usage: main.py [-h] [--mode {generate,label}] [--input INPUT] [--total TOTAL]
               [--output-dir OUTPUT_DIR] [--output-jsonl OUTPUT_JSONL]

Synthetic transaction narration pipeline.

options:
  -h, --help            show this help message and exit
  --mode {generate,label}
                        Pipeline mode: 'generate' to create dataset, 'label' to extract payee names. (default: generate)
  --input INPUT         CSV with real narration examples (Category,Narration) for generation mode. (default: transactions.csv)
  --total TOTAL         Target total narrations for generation mode.
  --output-dir OUTPUT_DIR
                        Output directory for all artifacts (output.jsonl, labels.jsonl, checkpoint files). (default: data)
  --output-jsonl OUTPUT_JSONL
                        Optional path to output.jsonl to label (defaults to <output-dir>/output.jsonl).
```

### Mode 1: Generation (`generate`)

Generates synthetic transaction narration strings, verifies them, deduplicates, and saves them.

```bash
python main.py --mode generate --input transactions.csv --total 10000
```
- **Outputs**:
  - `data/output.jsonl`: Contains the generated records with metadata (type, narration, latency, model, hash).
  - `data/checkpoint.json`: High-level summary of generation progress.

### Mode 2: Labeling (`label`)

Reads the generated `output.jsonl` dataset and invokes the Gemini model to extract the clean counterparty/payee names.

```bash
python main.py --mode label
```
- **Outputs**:
  - `data/labels.jsonl`: JSONLines containing the narration mapped to its extracted payee.
  - `data/label_checkpoint.json`: Checkpoint of labeled indices.

---

## Configuration Settings

You can customize the script behavior using environment variables (or setting them in a `.env` file):

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API Key | *Required* |
| `GEMINI_MODEL` | Specific model to target (e.g. `gemma-3-27b-it`, `gemini-2.0-flash`). Set to `AUTO` to automatically resolve to the closest instruction-tuned Gemma model available. | `AUTO` |
| `GEMINI_RPM` | Maximum API requests per minute (Rate Limit) | `60` |
| `GEMINI_MAX_CONCURRENCY` | Maximum concurrent API tasks/workers | `8` |
| `GEMINI_TIMEOUT_S` | API client request timeout in seconds | `60` |
| `OUTPUT_DIR` | Output folder path for generated files | `data` |
| `TARGET_TOTAL` | Default generation target count if `--total` is not specified | `10000` |
| `LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |

---

## Resume & Recovery Behavior

If the generation or labeling process is interrupted (e.g. CLI termination, network loss, system reboot):
1. The pipeline reads the current `output.jsonl` or `labels.jsonl` upon relaunch.
2. It rebuilds the deduplication set and exact counts directly from the files to guarantee data integrity.
3. It resumes the pipeline seamlessly from where it left off, avoiding unnecessary API calls.
