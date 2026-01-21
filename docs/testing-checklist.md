# Testing Checklist (Manual Run Log)
Last updated: 2026-01-05

Legend:
- [ ] Not run
- [x] Passed
- [!] Failed / needs follow-up

Notes:
- This file is updated as tests are executed.
- Evidence should capture the key output/verification query result.

## 0) Environment / Setup
- [x] Python deps installed (`python -m pip install -r requirements.txt`)
  - Evidence: pip install completed without errors.
- [x] API server starts (`uvicorn app.main:app --reload --port 8000`)
  - Evidence: server prints "Application startup complete."
- [x] Supabase env vars set in shell (SUPABASE_URL, SUPABASE_KEY)
  - Evidence: `echo $SUPABASE_URL` and `echo $SUPABASE_KEY` returned values.

## 1) FastAPI Health
- [x] GET /health
  - Command: `curl http://127.0.0.1:8000/health`
  - Evidence: `{"status":"ok"}`

## 2) Intake API - Text
- [x] POST /intake/text inserts rows
  - Command: `curl -X POST http://127.0.0.1:8000/intake/text -H "Content-Type: application/json" -d '{"title":"Test","text":"Chapter 1\nHello world.\nChapter 2\nMore text."}'`
  - Evidence: `{"status":"ok","inserted":2,...}`
- [x] Supabase rows created for manual intake
  - Query:
    - `select id, source_url, title from articles order by created_at desc limit 2;`
  - Evidence: two rows with titles `Chapter 1` and `Chapter 2`.

## 3) Intake API - File
- [x] POST /intake/file accepts PDF
  - Command: `curl -X POST http://127.0.0.1:8000/intake/file -F "title=Steven Meighan PhD" -F "file=@/c/Users/kladismo/Downloads/Steven Meighan PhD.pdf"`
  - Evidence: `{"status":"ok","inserted":22,...}`
- [x] POST /intake/file accepts DOCX
  - Command: `curl -X POST http://127.0.0.1:8000/intake/file -F "title=O dizajnoch" -F "file=@/c/Users/kladismo/Downloads/O dizajnoch.docx"`
  - Evidence: `{"status":"ok","inserted":1,...}`
- [x] POST /intake/file accepts TXT
  - Command: `curl -X POST http://127.0.0.1:8000/intake/file -F "title=Economist Upload" -F "file=@/c/Users/kladismo/Desktop/Work/Coding/Bachelor/Thesis/sources/_meta/Economist.txt"`
  - Evidence: `{"status":"ok","inserted":1,...}`
- [x] Supabase rows created for file intake
  - Query: `select id, source_url, title from articles where source_url like 'manual:%' order by created_at desc limit 1;`
  - Evidence: row with `source_url = manual:manual-upload:...` and title `Manual Upload`.
  - PDF spot-check query: `select id, source_url, title, created_at from articles where id = 'd04bd76a-537f-428f-a498-21a93e445377';`
  - Evidence: row returned with title `Intro` and created_at `2026-01-05 10:23:39.323223+00`.
  - DOCX spot-check query: `select id, source_url, title, created_at from articles where id = '9db19d6b-4467-4f67-b8d2-ef6783ba9e0b';`
  - Evidence: row returned with title `Manual Upload` and created_at `2026-01-05 10:26:36.866108+00`.

## 4) Scraper Worker
- [ ] Scrape sources (`python -m app.worker scrape --project-id <id>`)
  - Evidence: `scraped_total=<n>`
- [ ] Supabase: source_items populated
  - Query: `select count(*) from source_items;`
  - Evidence:
- [ ] Ingest source items (`python -m app.worker ingest-sources --project-id <id>`)
  - Evidence: `ingested_sources=<n>`
- [ ] Supabase: articles populated from sources
  - Query: `select count(*) from articles where source_website != 'manual';`
  - Evidence:

## 5) Extraction Worker (AI)
- [x] Run extraction (`python -m app.worker extract`)
  - Evidence: `extracted=3` (run twice for total 6).
  - Previous issues: HTTP 400 (max_tokens), empty content due to reasoning tokens, unsupported reasoning_effort value `none`.
  - Note: Added script fallback summary when LLM fails or is disabled.
- [x] Supabase: articles.processed = true
  - Query: `select id, source_url, processed, summary, length(content) as content_len from articles where processed = true order by scraped_at desc limit 3;`
  - Evidence: processed = true, summaries populated, content_len > 0.

## 6) First Judge (AI)
- [x] Run first judge (`python -m app.worker judge`)
  - Evidence: `judged=13`
- [x] Supabase: articles.scored = true with judge_score + format_assignments
  - Query: `select id, scored, judge_score, format_assignments from articles where scored = true order by scraped_at desc limit 3;`
  - Evidence: scored=true, judge_score populated, format_assignments present.

## 7) Generation (AI)
- [x] Run generation (`python -m app.worker generate`)
  - Evidence: `generated_posts=12`
  - Previous issue: OpenAI read timeout (request_timeout=30s) during generation.
- [ ] Supabase: video-only posts inserted with variant_id
  - Query: `select id, content_type, generating_model, content from posts order by created_at desc limit 3;`
  - Evidence: content_type=video, generating_model=gpt-5-mini, content includes variant_id.

## 8) Second Judge (AI)
- [x] Run second judge (`python -m app.worker second-judge`)
  - Evidence: `second_judged=5`
- [!] Note: OpenAI error (reasoning_effort 'minimal' unsupported for gpt-5.2; switched to 'low')
- [x] Supabase: posts.selected = true for winners (by variant_id)
  - Evidence: selected=true present on video posts after judging.
- [ ] Supabase: model_performance updated (if RPC available)
  - Evidence:

## 9) Audio Roundup (AI)
- [x] Run audio roundup (`python -m app.worker audio-roundup`)
  - Evidence: `audio_roundup=1`
- [x] Supabase: audio_roundup post inserted
  - Evidence: content_type=audio_roundup, generating_model=gpt-5-mini.
- [x] Render audio roundup to MP3 (`python -m app.worker render-audio-roundup`)
  - Evidence: `audio_roundup_rendered=1 path=media_out\\audio_roundup_db944425-ccb4-4413-ab0e-464e24f57c91.mp3`

## 10) Media Helpers (Optional)
- [x] Placeholder images generate (`app/media/video.py:create_placeholder_images`)
  - Evidence: `scene_01.png` etc. created in `media_out/tmp_video` when image gen fails.
- [x] Render short video (`python -m app.worker render-video`)
  - Evidence: `video_rendered=1 path=media_out\\video_80943106-3ae6-42af-83a4-4c72c73a1935.mp4`
  - Note: Image generation returned 403 (OpenAI images access/billing), so placeholders used.
- [ ] Karaoke captions (ASS) aligned to TTS (`ENABLE_ASR=true`)
  - Evidence:
