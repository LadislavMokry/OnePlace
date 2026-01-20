# Content Automation - Implementation Plan (Python-first)
Last updated: 2026-01-20

## Scope
- Python-first system (FastAPI + worker scripts).
- Video-first outputs (shorts + audio roundup). Multi-format outputs are deferred.
- Project-based sources (RSS, Reddit, page, YouTube) managed in the Admin UI.
- Storage: Supabase (projects, sources, source_items, articles, posts, article_usage, youtube_accounts).

## Current Status (Summary)
- Admin UI + API endpoints are in place (`app/main.py`, `assets/admin.html`).
- Scrape -> ingest -> extract -> judge -> dedupe/unusable pipeline exists.
- Video generation + second judge + audio roundup are implemented.
- Audio/video rendering works with FFmpeg. Image generation depends on OpenAI Images access.
- Cleanup worker added (retention for source_items, legacy tables, and unusable articles).
- Hetzner server provisioned (see `docs/server-notes.md`).

---

## Architecture

### Components
- **API + Admin UI**: FastAPI app with project/source management and pipeline triggers.
- **Workers**: CLI runner (`python -m app.worker ...`) for scraping, extraction, judging, generation, and rendering.
- **AI Modules**: OpenAI client + extraction/judge/generation/audio roundup.
- **Media**: FFmpeg-based audio + video rendering.
- **Storage**: Supabase tables and helpers in `db/supabase-schema.sql`.

### Pipeline Flow
1. **Scrape sources** -> `source_items`
2. **Ingest items** -> `articles` (dedupe + full text fetch)
3. **Extract** -> `summary`, `processed = true`
4. **First judge** -> `judge_score`, `format_assignments`
5. **Deduplicate / unusable** -> mark duplicates + low-score/old
6. **Generate video variants** -> `posts`
7. **Second judge** -> choose best variant (`selected = true`)
8. **Audio roundup** -> `posts` + `article_usage`
9. **Render media** -> MP3/MP4 assets in `media_out/`

---

## Phase 0: Environment & Database
- [ ] Ensure `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY` are set.
- [ ] Apply schema in `db/supabase-schema.sql`.
- [ ] Verify core tables and columns exist (projects/sources/source_items/articles/posts/article_usage).
- [ ] Install FFmpeg on host.

---

## Phase 1: Projects & Sources
- [ ] Seed projects (5 initial topics) in Admin UI or scripts.
- [ ] Add RSS/Reddit/Google News sources to each project.
- [ ] Use **Check All** to detect login walls.
- [ ] Validate scraping + ingestion for each project.

---

## Phase 2: Core Pipeline
- [ ] Run **Run Pipeline** in Admin UI per project.
- [ ] Verify `articles.processed` and `articles.scored`.
- [ ] Verify `dedupe` and `unusable` logic.
- [ ] Confirm generation writes `posts` (video variants).
- [ ] Run second judge and confirm `selected = true`.

---

## Phase 3: Media Rendering
- [ ] Render audio roundup MP3.
- [ ] Render audio roundup MP4.
- [ ] Render short video MP4.
- [ ] Fix image generation access (OpenAI Images) or choose alternate source.

---

## Phase 4: Scheduling & Retention
- [ ] Add systemd services:
  - API (`uvicorn app.main:app`)
  - Worker pipeline loop(s)
- [ ] Add systemd timers:
  - Pipeline run (hourly or per project cadence)
  - Cleanup every 48 hours (`python -m app.worker cleanup --hours 48`)
- [ ] Validate cleanup retention behavior (source_items + unusable content).

---

## Phase 5: Publishing & Metrics (Future)
- [ ] Implement platform posting workers.
- [ ] Add OAuth flows for YouTube.
- [ ] Add metrics ingestion (YouTube first).
- [ ] Add cost tracking per provider.

---

## Verification Checklist
- [ ] `/health` returns ok.
- [ ] Admin UI lists projects and sources.
- [ ] Pipeline completes for at least one project.
- [ ] Audio roundup script renders to MP3 and MP4.
- [ ] Short video renders with captions.

