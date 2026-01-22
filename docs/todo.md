# Content Automation - Task List (Python)
Last updated: 2026-01-20

Legend:
- [ ] Not started
- [→] In progress
- [✓] Done
- [✗] Blocked

---

## Current Status
- [✓] Supabase schema updated (projects/sources/source_items/articles/posts/article_usage).
- [✓] Admin UI + Stats UI in place.
- [✓] Pipeline steps implemented (scrape, ingest, extract, judge, generate, second judge).
- [✓] Audio roundup generation + render (MP3/MP4).
- [✓] Short video rendering (FFmpeg).
- [✓] Cleanup worker added (retention policy).
- [→] Server deployment (Hetzner) in progress.
- [ ] Define per-project funnel strategy (short-form -> daily 7-10 min paid podcast).

---

## Deployment (Server)
- [→] Clone repo to server
- [ ] Create `.env.local` on server with Supabase + OpenAI keys
- [ ] Create Python venv + install `requirements.txt`
- [ ] Run API (systemd service)
- [ ] Run pipeline + media workers (systemd timers)
- [ ] Validate `/health` and Admin UI on server

---

## Ingestion & Pipeline
- [ ] Seed projects + sources in Admin UI
- [ ] Check source access for login walls
- [ ] Note: Reddit sources now require an auth cookie to avoid 403 blocking (set via Source "Login" config).
- [ ] Run pipeline per project (scrape -> ingest -> extract -> judge -> dedupe/unusable)
- [ ] Verify `articles.processed` + `articles.scored`
- [ ] Verify `posts` for video variants + `selected = true`
- [ ] Generate audio roundup and render

---

## Media Rendering
- [ ] Confirm FFmpeg works on server
- [ ] Resolve OpenAI Images 403 (enable billing or alternate provider)
- [ ] Verify short video images (not placeholders)
- [ ] Verify karaoke captions (ENABLE_ASR)

---

## Scheduling & Retention
- [ ] Add systemd timers for:
  - Pipeline cadence (hourly or per project)
  - Generation + second judge (staggered)
  - Audio roundup (daily)
  - Cleanup every 48 hours
- [ ] Verify cleanup wipes unusable content + removes old source_items

---

## Publishing & Metrics (Future)
- [ ] Add YouTube OAuth upload worker
- [ ] Add posting worker + rate limiting
- [ ] Add metrics ingestion (YouTube first)
- [ ] Add cost tracking in stats view
- [ ] Add subscription CTA tracking (short-form -> podcast conversion)
