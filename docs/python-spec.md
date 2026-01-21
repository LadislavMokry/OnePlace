# Python Content Automation Spec (Deep)
Last Updated: 2026-01-05
Target Platform: Python (FastAPI + worker scripts)
Storage: Supabase
Scope: Manual intake + scraping -> extraction + judging -> video/audio generation -> publishing

---

1. Overview

1.1 Goal
Build a Python-first system that ingests text (upload/paste) and scraped pages, then runs extraction, judging, and content generation for video-first outputs. The MVP is topic-agnostic.

1.2 High-Level Flow
Manual Intake (upload/paste) -> articles
Scraping (sources) -> source_items -> articles
Extraction (content + summary) -> articles
First Judge (score) -> articles
Generation (video-only variants) -> posts
Second Judge (pick best variant) -> posts
Publishing -> posts
Performance Tracking -> performance_metrics / model_performance

1.3 Design Principles
- Modular: each stage is an independent worker
- Idempotent: safe to re-run jobs
- Cost-aware: batching, prompt caching
- Observable: logs + minimal metrics

---

2. Architecture

2.1 Services
- API: FastAPI for manual intake
- Workers: cron or loop processes for scraping and AI pipeline
- Storage: Supabase Postgres + Storage (optional)

2.2 Code Layout
- app/main.py (API)
- app/ingest.py (split + extract helpers)
- app/scrape.py (scraper)
- app/worker.py (runner)
- app/ai/* (extract, judge, generate, second-judge)

2.3 Deployment Model
- VPS preferred for scraping stability
- API runs as systemd service
- Workers run via cron or systemd timers
- During testing: run workers manually (no schedule)

---

3. Data Model (Supabase)

3.1 articles
Purpose: canonical content items (manual or scraped)
Key fields:
- id (uuid)
- source_url (unique)
- source_website (manual or domain)
- title
- raw_html (raw HTML or extracted text)
- content (extracted article text)
- summary (LLM or fallback summary)
- judge_score (1-10)
- format_assignments (jsonb array, video-only gate for now)
- processed, scored (bool)
- scraped_at, created_at

3.2 posts
Purpose: AI-generated content per article + output type
Key fields:
- article_id
- platform
- content_type (video, audio_roundup)
- generating_model
- content (jsonb)
- selected

3.3 performance_metrics
Purpose: engagement tracking

3.4 model_performance
Purpose: track model wins over time

---

4. Intake API

4.1 Endpoints
- GET /health
- POST /intake/text
- POST /intake/file

4.2 /intake/text
Request JSON:
{
  "title": "Optional",
  "text": "Required"
}
Behavior:
- Validate text
- Split by headings
- Fallback chunk by MAX_WORDS
- Insert each chunk into articles

4.3 /intake/file
Request multipart:
- title (optional)
- file (required)
Behavior:
- Save file to temp
- Run scripts/extract_text.py
- Parse sections
- Insert each chunk into articles

4.4 Response
- status: ok
- inserted: count
- ids: list of article ids

---

5. Scraping

5.1 Sources
MVP list (configurable):
- https://www.topky.sk/se/15/Prominenti
- https://www.cas.sk/r/prominenti
- https://www1.pluska.sk/r/soubiznis
- https://refresher.sk/osobnosti
- https://www.startitup.sk/kategoria/kultura/

5.2 Behavior
- Scrape project sources (RSS/Reddit/page/YouTube) -> source_items
- Ingest source_items -> articles (full-text fetch + URL normalization + dedupe)
- Use unique constraints to prevent duplicates

5.3 Error Handling
- On non-200: log and continue
- On timeout: retry optional

---

6. Extraction Worker (Implemented)

Inputs:
- articles where processed=false
Outputs:
- content, summary, processed=true

Rules:
- Use trafilatura to extract main article content
- Fallback to basic HTML stripping if extraction fails
- Truncate to EXTRACTION_MAX_CHARS
- If EXTRACTION_USE_LLM=false or LLM fails, use a fallback summary

---

7. First Judge (Implemented)

Inputs:
- articles where processed=true and scored=false
Outputs:
- judge_score, format_assignments, scored=true

Rules:
- Score 1-10 based on summary
- Gate for video-only output:
  - score >= 6 => ["video"]
  - score < 6 => []

---

8. Generation (In Progress)

Inputs:
- articles with video gate (score >= 6 or format_assignments contains "video")
Outputs:
- posts rows per variant

Constraints:
- Use full article content (not summary) for generation
- Video-only JSON schema (script, scenes[], captions[], duration_seconds)
- Generate N variants per article (default 3), same model

---

9. Second Judge (In Progress)

Inputs:
- posts grouped by article + content_type + variant_id
Outputs:
- best selected per group

---

10. Publishing (Planned)

Targets:
- TikTok, Instagram Reels, Facebook Reels (video-first)
- YouTube (optional for shorts and audio roundup)

Constraints:
- rate limits per platform
- store post_url, posted_at

10.1 Short Video Automation (Planned)
Goal: 45-60 second vertical videos (9:16).
Pipeline:
- Generate script from content
- Split into 8-10 scenes
- Generate or extract images per scene (low-cost)
- Generate voiceover (TTS)
- Generate word-level captions (ASR or aligned script)
- Assemble with FFmpeg (images + voice + captions + Ken Burns)
Requirement: FFmpeg installed on host

10.2 Audio Roundup (Planned)
Goal: 3-5 minute audio episode with 5 stories.
Pipeline:
- Select top 5 scored articles in window
- Generate two-host dialogue (male + female)
- Generate two-voice TTS
- Assemble audio + optional visualizer video

---

11. Monitoring + Testing

11.1 Basic API Tests
- /health ok
- /intake/text inserts rows
- /intake/file inserts rows

11.2 Scraper Tests
- scrape inserts rows
- partial failures do not stop job

11.3 Data Tests
- source_url unique
- processed/scored defaults false

---

12. Configuration
Required:
- SUPABASE_URL
- SUPABASE_KEY

Optional:
- OPENAI_API_KEY
- MANUAL_INTAKE_SCRIPT
- MANUAL_INTAKE_DIR
- MAX_WORDS
- REQUEST_TIMEOUT
- EXTRACTION_MAX_CHARS
- EXTRACTION_USE_LLM
- EXTRACTION_MODEL
- JUDGE_MODEL
- SECOND_JUDGE_MODEL
- GENERATION_MODELS
- TTS_MODEL
- ASR_MODEL
- IMAGE_MODEL
- ENABLE_TTS
- ENABLE_ASR
- ENABLE_IMAGE_GENERATION

---

13. Decisions + Open Questions

Decisions
- Start with source scraping (RSS/Reddit/page/YouTube). Social/video scraping deferred.
- Video-first outputs: one-story shorts + optional audio roundup.
- Video format: 9:16 vertical with captions and Ken Burns motion.
- Use OpenAI models for early testing; finalize model list later.

Open Questions
- Exact website sources list for MVP
- Final model lineup for extraction/judging/generation/tts
- Publishing platform priority (TikTok/IG Reels/Facebook first?)
- Token/cost budgets per stage
- Best voices for Slovak two-host audio

