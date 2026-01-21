# Python Architecture Overview
**Last Updated:** 2026-01-05

## Summary
This project uses a Python-first architecture:
- **FastAPI** for intake (text + file uploads)
- **Worker scripts** for scraping, extraction, judging, and generation
- **Supabase** for storage
- **AI APIs** for summaries/judging + media generation
- **Video-first outputs** (short-form video + optional audio roundup)

---

## Components

### 1) Intake API
**Entry points**
- `POST /intake/text` — JSON `{title, text}`
- `POST /intake/file` — multipart form `title` + `file`

**Code**
- `app/main.py`
- `app/ingest.py`

---

### 2) Scraper Worker
**Purpose**: Scrape project sources (RSS/Reddit/YouTube/page) into `source_items`, then ingest to `articles`.

**Code**
- `app/admin.py` (project/source scraping + ingest)
- `app/worker.py`

**Run**
```bash
python -m app.worker scrape --project-id <project_id>
python -m app.worker scrape-loop --interval 3600 --project-id <project_id>
python -m app.worker ingest-sources --project-id <project_id>
python -m app.worker extract
python -m app.worker judge
python -m app.worker generate
python -m app.worker second-judge
python -m app.worker audio-roundup
```

**Note**: The legacy category-page scraper in `app/scrape.py` is deprecated.

---

### 3) AI Workers
**Purpose**: Summarize, score, generate content, and pick best variants.

**Modules**
- `app/ai/extract.py` (trafilatura + summary)
- `app/ai/first_judge.py`
- `app/ai/generate.py` (video-only output)
- `app/ai/second_judge.py`

---

## Local Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

## Deployment (VPS)
1. `git clone` repo
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Set env vars: `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY`
5. Run API as a service (systemd) and worker via cron or service loop

---

## Environment Variables
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `OPENAI_API_KEY` (for AI workers)
- `MANUAL_INTAKE_SCRIPT` (defaults to `scripts/extract_text.py`)
- `MANUAL_INTAKE_DIR` (optional temp dir override)
- `MAX_WORDS` (default 2500)
- `REQUEST_TIMEOUT` (default 30)
- `EXTRACTION_MAX_CHARS` (default 20000)
- `EXTRACTION_USE_LLM` (default true; fallback summary if false)
- `EXTRACTION_MODEL`, `JUDGE_MODEL`, `SECOND_JUDGE_MODEL`, `GENERATION_MODELS`
- `TTS_MODEL`, `ASR_MODEL`, `IMAGE_MODEL`
- `ENABLE_TTS`, `ENABLE_ASR`, `ENABLE_IMAGE_GENERATION`
