# Handoff Notes
Last updated: 2026-01-19

## Launch prep (remainder / what’s left before going live)
1. Verify end-to-end pipeline per project (scrape → ingest → extract → score → audio roundup → render audio/video).
2. Add scheduling (daily runs per project; retries + basic logging).
3. Create platform accounts (YouTube channels per topic; optional Meta pages + TikTok accounts).
4. Connect metrics (start with YouTube analytics; add Meta/TikTok later).

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
- Need to run DB migrations for new columns/tables (see `db/supabase-schema.sql`).
  - At minimum: add `articles.source_id`.
- Stats only count articles ingested after `source_id` exists (older articles need backfill if desired).

## Next steps (recommended)
1. Re-run pipeline and verify articles get scored + appear in Articles & Scores.
2. Test audio roundup generation (Generate Script → Render Audio) after scoring completes.
3. Validate `/stats` page and decide whether to backfill older articles with `source_id`.
4. Implement auto-scheduling for pipeline + audio roundup (set-and-forget).
5. Test generating + plan automation for uploading and post-performance stats ingestion.
6. Brainstorm social strategy + monetization plan; plan how to automate social account setup (or decide manual process).

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
- OpenAI images API returns **403 Forbidden** for `/v1/images/generations`.
  - Result: video renders with placeholder images (black background + text).
  - Likely due to missing Images access/billing on the API key.

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
