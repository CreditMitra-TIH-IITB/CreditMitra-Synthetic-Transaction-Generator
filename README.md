# Synthetic Transaction Narration Generator (India)

Production-grade Python pipeline to generate **10,000** highly realistic Indian bank transaction narrations using **Gemma 27B** via the **Gemini API**, with **ONE LLM call per narration** (no batching), **deduplication**, and **crash-safe resume**.

## What it does

- Loads **25 real narration examples** from `transactions.csv` (or an optional custom CSV).
- Generates **exactly one narration per API call**.
- Enforces target distribution:
  - **90%** P2P (person-to-person)
  - **10%** merchant
- Validates + deduplicates each narration.
- **Persists immediately** after each accepted narration:
  - append-only `data/output.jsonl`
  - `data/checkpoint.json` updated after every write
- On restart: rebuilds dedupe set from existing `output.jsonl` and resumes without regenerating old entries.

## Setup

### 1) Install

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Configure environment

Set your Gemini API key (required):

- PowerShell:

```powershell
$env:GEMINI_API_KEY="YOUR_KEY"
```

Optional overrides:

- `GEMINI_MODEL` (default: `gemma-2-27b-it`)
- `GEMINI_RPM` requests/minute throttle (default: `60`)
- `GEMINI_MAX_CONCURRENCY` (default: `8`)
- `OUTPUT_DIR` (default: `data`)
- `TARGET_TOTAL` (default: `10000`)

## Run

```bash
python main.py --input transactions.csv --total 10000
```

Outputs:

- `data/output.jsonl` (append-only, resume-safe)
- `data/checkpoint.json`

## Resume behavior

If the process crashes or you stop it:

- Re-running the same command will:
  - read `data/output.jsonl`
  - rebuild the dedupe hash set
  - load/update `data/checkpoint.json`
  - continue generating until the target total is reached

## Notes on “one call per narration”

This system **never batches multiple narrations into one request**. Every request is asked to return **exactly one** narration string.

If a response is invalid or duplicates an existing narration, the job is retried (which necessarily requires another single-narration call). This preserves the strict “**one narration per API call**” constraint while meeting uniqueness/validation requirements.

