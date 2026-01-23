# Handoff Notes
Last updated: 2026-01-22

## Summary of this session (2026-01-21)
- YouTube uploads enabled end-to-end for audio roundups (OAuth stored in `youtube_accounts`).
- Added YouTube upload worker + systemd timer (`oneplace-youtube-upload.timer` at 07:00 UTC).
- Added YouTube Analytics daily metrics + `/stats` UI section.
- Added per-video YouTube checkpoint metrics (1h, 12h, 24h, 3d, 7d, 14d, 30d) + `/stats` UI section with LLM/TTS metadata.
- Added `youtube_metrics` + `youtube_video_metrics` tables and DB patches.
- Added YouTube analytics worker commands:
  - `python -m app.worker youtube-analytics`
  - `python -m app.worker youtube-video-metrics`
- Fixed YouTube upload metadata sanitization (avoid empty titles).

## Summary of this session (2026-01-20)
- Verified Supabase schema is up to date using existing .env.local keys.
- Cleaned legacy data:
  - Deleted all rows from `category_pages` and `article_urls`.
  - Deleted `articles` where `project_id IS NULL` (left project-scoped articles intact).
- Added cleanup worker step to delete old `source_items` and wipe unusable article content after a retention window (see `app/pipeline.py` + `app/worker.py`).
- Provisioned Hetzner Cloud server (see `docs/server-notes.md`) and installed base dependencies (git, python3-venv, python3-pip, ffmpeg).
- Removed legacy n8n folders/files (`workflows/`, `n8n-skills/`, `CLAUDE.md`, `assets/manual-intake.html`, `docs/scraper-workflow-quick-start.md`).
- Rewrote `docs/implementation-plan.md` + `docs/todo.md` to reflect the Python-first/server approach.
- Added pipeline run logging:
  - New `pipeline_runs` table added to `db/supabase-schema.sql`
  - Patch file created: `db/patches/2026-01-20-pipeline-runs.sql`
  - Pipeline logging implemented in `app/pipeline.py`
  - New worker command: `python -m app.worker pipeline`
- Added per-source scrape interval checks (`scrape_interval_hours`) to skip frequent scrapes.
- Set up server services + timers:
  - `oneplace-api.service` (Uvicorn on 0.0.0.0:8000)
  - `oneplace-cleanup.timer` (every 48 hours)
  - `oneplace-pipeline.timer` (every 3 hours)
  - `oneplace-generate.timer` (daily 06:10 UTC)
  - `oneplace-second-judge.timer` (daily 06:25 UTC)
  - `oneplace-audio-roundup.timer` (daily 06:40 UTC)
  - `oneplace-render-roundup.timer` (daily 06:50 UTC)
- Installed Nginx + basic auth (Laco / 290198150896) and proxy on port 80.
- Server `.env.local` set with SUPABASE_URL / SUPABASE_KEY / OPENAI_API_KEY.
- Requirements updated with `lxml_html_clean` to fix trafilatura import.
- `media_out/` is now ignored by Git.
- Server access: added new desktop SSH key and verified login from desktop.

## Launch prep (remainder / what’s left before going live)
1. Verify end-to-end pipeline per project (scrape → ingest → extract → score → audio roundup → render audio/video).
2. Add scheduling (daily runs per project; retries + basic logging).
3. Create platform accounts (YouTube channels per topic; optional Meta pages + TikTok accounts).
4. Connect metrics (start with YouTube analytics; add Meta/TikTok later).
5. Evaluate alt LLM providers for script quality/virality (Claude, xAI, Gemini).

## Current launch configuration
- Topics (EN-only for now):
  - Celebrities / Entertainment
  - TV & Streaming Recaps
  - Sports (results + storylines)
  - Viral / Human-interest
  - Nostalgia / Pop-culture history
- Projects for the 5 topics created in Supabase (seeded).
- Sources seeded (RSS + Reddit link posts + Google News RSS per topic).
- Audio roundup now uses full article content (truncated to fit limits).
- Audio roundup script targets 5–7 minutes with a teaser rundown of all stories first.
- Audio roundup generates an image prompt for a static episode thumbnail.
- New media layout: per-post folders under `media_out/roundup/{post_id}/`.
- Temp render assets now auto-clean after successful render.

## Summary of this session (2026-01-18)
- Added F1 sources to project and expanded Admin UI for inline item viewing + auth management per source.
- Source auth: login panel with basic/cookie/header options; auto-detect login walls; Check All button with spinner.
- New ingest flow: source_items → full article text (trafilatura) → articles; URL normalization + content hash dedupe.
- Pipeline button in UI runs: scrape → ingest → extract → score → dedupe → expire (loops until empty with caps).
- Project settings: configurable unusable thresholds (score + age hours); displayed per-project inputs.
- Articles & Scores table: pagination, ordering, used/unusable flags; unscored items sorted last.
- Usage tracking: added `article_usage` table and marking for audio roundups.
- Added `/stats` page + API for source hit-rate (% of articles used in audio roundup) and avg score per source.
- Added `articles.source_id` to track source-level stats.

## Current blockers / open issues
- [Fixed 2026-01-20] DB migrations applied for new columns/tables (see `db/supabase-schema.sql`), including `articles.source_id`.
- Stats only count articles ingested after `source_id` exists (older articles need backfill if desired).
- [Fixed 2026-01-20] OpenAI Images access resolved; images now generate successfully.

## Next steps (recommended)
1. Create the other 4 YouTube brand channels once the account is verified; run OAuth per channel and save refresh tokens in `youtube_accounts`.
2. Add other LLM script providers for A/B tests: Anthropic, xAI, Google.
3. Add Inworld AI TTS with A/B test voices: Ashley, Deborah, Dennis, Edward, Sarah, Timothy.
4. Add a daily timer for `youtube-video-metrics` (checkpoint collection).
5. At next session start: check systemd timers ran and review `/var/log/oneplace/*.log` for failures.

## Summary of this session (2026-01-17, later)
- Admin UI JS refactor: cached DOM refs, event delegation for source actions, shared helpers, and safer HTML rendering.
- Reddit scraping upgraded: top posts via JSON listing, article extraction for link posts, optional image captioning for image posts.
- New image caption helper + OpenAI client support for image input.
- New config flags: `ENABLE_IMAGE_CAPTION` and `IMAGE_CAPTION_MODEL`.

## Next steps (tomorrow)
1. Manually add F1 sources (RSS + Reddit) in the admin view.
2. Test scraping and verify items show up for each source.

## Notes / requirements
- Image captioning requires `ENABLE_IMAGE_CAPTION=true` and a valid `OPENAI_API_KEY`.

## Summary of this session (2026-01-17)
- Admin UI renamed to **OnePlace Admin**.
- Project settings added: language (dropdown: en/es/sk) + generation interval hours.
- Source settings added: scrape interval hours.
- Project delete implemented (UI + API).
- Audio Roundup UI added: generate script + render audio + preview player.
- Audio roundup generation now respects project language (only at script generation stage).
- New API endpoints:
  - `POST /api/projects/{project_id}/audio-roundup`
  - `POST /api/audio-roundup/{post_id}/render`
  - `GET /api/audio-roundup/{post_id}/audio`
  - `DELETE /api/projects/{project_id}`
- Schema updates (added columns): `projects.language`, `projects.generation_interval_hours`, `projects.last_generated_at`, `sources.scrape_interval_hours`.
- Added TODO: per-language TTS model/voice selection (plan for ElevenLabs).
- Added `docs/startup-guide.md`.

## Current blockers / open issues
- FFmpeg not installed on user’s Windows machine yet; required for audio render.
- TTS requires `ENABLE_TTS=true` and a valid `OPENAI_API_KEY`.

## Next steps (recommended)
1. Install FFmpeg (e.g., `winget install --id=Gyan.FFmpeg`) and restart terminal/IDE.
2. Verify `ffmpeg -version` works.
3. In UI: select project language → Save Settings → Generate Script → Render Audio → preview.
4. Add F1 project sources and test scraping.

## Notable code changes in this session
- `assets/admin.html`: language dropdown, intervals, delete project, audio roundup panel, OnePlace title.
- `app/main.py`: new audio roundup + delete project endpoints, audio file serving.
- `app/admin.py`: create/update project/source extended; delete project.
- `app/ai/audio_roundup.py`: language-aware system prompt.
- `app/pipeline.py`: `run_audio_roundup` supports project_id/language.
- `app/worker.py`: `audio-roundup` CLI supports `--project-id`/`--language`.
- `db/supabase-schema.sql`: new columns + safe ALTERs.
- `docs/todo.md`: ElevenLabs/per-language TTS note.
- `docs/startup-guide.md`: quickstart commands.

---

## Summary of this session

## Summary of this session
- End-to-end pipeline tested: scrape → extract → judge → generate → second-judge → audio-roundup → render-audio-roundup → render-video.
- Video render now completes and writes MP4 to `media_out/`.
- Karaoke-style captions implemented via ASS + ASR word timestamps, with fallback to script timing when ASR has no words.
- Image generation call switched to OpenAI image generations endpoint, portrait size used, and failures are logged.
- Audio roundup render works after FFmpeg install.
- `docs/testing-checklist.md` updated to reflect passing render steps and the image 403 note.

## Current blockers / open issues
- [Fixed 2026-01-20] OpenAI Images access resolved; `/v1/images/generations` now works and renders real images.

## What works now (verified)
- `python -m app.worker render-audio-roundup` → MP3 created in `media_out/`.
- `python -m app.worker render-video` → MP4 created in `media_out/` (placeholders if images are blocked).

## Next steps (recommended order)
1. **Fix image generation access**  
   - Enable OpenAI Images access/billing for the API key, or use a different key.  
   - Then rerun:
     - `rm -rf media_out/tmp_video`
     - `python -m app.worker render-video`
2. **Verify karaoke captions**
   - Confirm `media_out/tmp_video/captions.ass` exists after render.
   - Watch the MP4 to verify word highlighting.
3. **Optional: add image fallback**
   - If images remain blocked, decide whether to keep placeholders or integrate a non-OpenAI image source.

## Notable code changes in this session
- `app/ai/openai_client.py`: image generation now uses `/images/generations` and GPT image settings.
- `app/media/short_video.py`: image generation logging + portrait size; ASS captions always written; ASR fallback.
- `docs/testing-checklist.md`: render-video marked as passed, with image 403 note.

## Useful commands
- Env sanity check:
  - `python -c "from app.config import get_settings; s=get_settings(); print('ENABLE_TTS=', s.enable_tts); print('ENABLE_ASR=', s.enable_asr); print('ENABLE_IMAGE_GENERATION=', s.enable_image_generation); print('TTS_MODEL=', s.tts_model); print('ASR_MODEL=', s.asr_model); print('IMAGE_MODEL=', s.image_model)"`
- Render audio roundup:
  - `python -m app.worker render-audio-roundup`
- Render video:
  - `rm -rf media_out/tmp_video`
  - `python -m app.worker render-video`

---

## In-progress notes (2026-01-22) – Resume here

### What we did
- **Added systemd timers/services** for YouTube analytics + video metrics:
  - `oneplace-youtube-analytics.timer` (daily 07:15 UTC)
  - `oneplace-youtube-video-metrics.timer` (hourly, randomized delay 5m)
  - Installed on server and enabled; manual smoke-test succeeded.
- **Upgraded server Python to 3.11** (new venv, reinstalled requirements). `oneplace-api.service` is running on Python 3.11.
- **Switched TTS provider to Inworld** on server via `.env.local`:
  - `TTS_PROVIDER=inworld`
  - `INWORLD_BASE64_KEY=...`
  - `TTS_MAX_CHARS=2000`
  - `ENABLE_TTS=true`
- Verified Inworld key by hitting **list voices** (HTTP 200).
- Verified **TTS synth works** with model `inworld-tts-1` and `inworld-tts-1.5-max` via curl.

### Current blocker: audio roundup render failure
### Audio roundup render failure – fixed
- Root cause was **fallback voices** on older posts:
  - Older audio-roundup posts lacked `tts_voice_a/b`, so renderer fell back to defaults (`onyx`/`nova`), which are **invalid** for Inworld.
  - Inworld returned HTTP 404 when asked to synthesize those voices.
- Fix applied on server:
  - `.env.local` updated with Inworld defaults:
    - `AUDIO_ROUNDUP_VOICE_A=Timothy`
    - `AUDIO_ROUNDUP_VOICE_B=Ashley`
    - `INWORLD_TTS_MODEL=inworld-tts-1.5-max`
- Manual render succeeded:
  - `/root/OnePlace/.venv/bin/python -m app.worker render-audio-roundup --all-projects`
  - Output ended with `audio_roundup_rendered_all=6`
- After manual success, restart service:
  - `sudo systemctl reset-failed oneplace-render-roundup.service`
  - `sudo systemctl restart oneplace-render-roundup.service`

### YouTube upload failure (unresolved)
- `oneplace-youtube-upload.service` failed when restarted after the Python upgrade.
- Journald output didn’t show the traceback; need to run manually to see real error:
  - `/root/OnePlace/.venv/bin/python -m app.worker youtube-upload --all-projects`
  - Paste the traceback and fix accordingly.

### Next session checklist
- Confirm `oneplace-render-roundup.service` completed successfully after restart:
  - `systemctl status oneplace-render-roundup.service --no-pager`
  - `journalctl -u oneplace-render-roundup.service --since "today" --no-pager`

### Server status checks
- Timers list now includes:
  - pipeline, generate, second-judge, audio-roundup, render-roundup, youtube-upload, cleanup
  - **new**: youtube-analytics, youtube-video-metrics
- Commands used:
  - `systemctl list-timers --all | grep oneplace`
  - `systemctl status oneplace-*.service --no-pager`
  - `journalctl -u oneplace-*.service --since "24 hours ago" --no-pager`

---

## Summary of this session (2026-01-23)
- **Podcast RSS + R2 publishing implemented**:
  - New R2 uploader + RSS generator + publish flow (audio + artwork + RSS).
  - New worker command: `python -m app.worker publish-podcast --all-projects`.
  - Podcast image prompts stored per project in `projects.podcast_image_prompt`.
  - Static project artwork is generated once and reused for all episodes.
- **R2 bucket** created: `oneplace-podcasts` with public base URL:
  - `https://pub-6bc969ff45954c90afbbfc3610c4592e.r2.dev`
- **RSS URLs (submit once to Apple + Spotify):**
  - `.../podcasts/celebrities-entertainment/rss.xml`
  - `.../podcasts/tv-streaming-recaps/rss.xml`
  - `.../podcasts/sports-results-storylines/rss.xml`
  - `.../podcasts/viral-human-interest/rss.xml`
  - `.../podcasts/nostalgia-pop-culture-history/rss.xml`
- **Audio roundup length extended**: target 10–15 minutes; default story count set to 8 (env override).
- **New systemd timer added** for podcast publishing:
  - `oneplace-podcast-publish.timer` (13:45 UTC).
- **Timers shifted to US-morning cadence (UTC):**
  - generate 12:30
  - second-judge 12:45
  - audio-roundup 13:15
  - render-roundup 13:30
  - podcast-publish 13:45
  - youtube-upload 14:00
  - youtube-analytics 14:15
- **Manual validation**: RSS reachable (200 OK) from server; publish succeeded.
- **RSS submitted**: Feeds submitted to Apple Podcasts Connect and Spotify for Podcasters.

## Notes / reminders
- Apple/Spotify pull RSS; they do **not** accept pushes. Submit each RSS once.
- Increase `REQUEST_TIMEOUT` (e.g., 120s) for 10–15 minute scripts to avoid OpenAI timeouts.
- `podcast_image_generated=5 missing_prompt=1` indicates an extra `f1` project without metadata.
- **YouTube channels**: 4 additional channels still need to be created + OAuth tokens stored per project.
