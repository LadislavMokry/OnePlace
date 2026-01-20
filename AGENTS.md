# Repository Guidelines

## Project Structure & Module Organization
This repo uses a Python-first architecture (FastAPI + worker scripts) for manual intake, scraping, extraction, scoring, and media generation.

- Python app: `app/` (FastAPI intake API + worker scripts).
- Database schema: `db/supabase-schema.sql` (tables for articles, posts, metrics).
- Guides and specs: `docs/SETUP-GUIDE.md`, `docs/slovak-gossip-automation-spec (1).md`, `docs/implementation-plan.md`, `docs/todo.md`, `docs/manual-intake.md`.

## Build, Test, and Development Commands
There is no build step or test runner in this repo.

- Install Python deps: `pip install -r requirements.txt`
- Run API locally: `uvicorn app.main:app --reload --port 8000`
- Run scraper once: `python -m app.worker scrape`
- Run scraper loop: `python -m app.worker scrape-loop --interval 3600`
- Run extraction: `python -m app.worker extract`
- Run first judge: `python -m app.worker judge`
- Run generation: `python -m app.worker generate`
- Run second judge: `python -m app.worker second-judge`
- Run audio roundup: `python -m app.worker audio-roundup`
- Apply schema by running `db/supabase-schema.sql` in the Supabase SQL Editor.

## Coding Style & Naming Conventions
- Python files use 4-space indentation.
- JSON files use 2-space indentation; keep exports consistent.

## Testing Guidelines
- Validate Supabase connectivity with a simple API call or SQL query.
- Smoke-test API endpoints: `/health`, `/intake/text`, `/intake/file`.
- Validate data with SQL queries in the Supabase dashboard.
- For media generation, ensure FFmpeg is available on the host.

## Commit & Pull Request Guidelines
- History uses short, sentence-style messages without a strict convention.
- Keep commits scoped and descriptive (example: `Add FastAPI intake endpoints`).
- PRs should include: summary, schema changes (if any), and test notes.

## Security & Configuration Tips
- Store secrets in `.env` or `.env.local`; never commit API keys.
- `.env` / `.env.local` are auto-loaded by the Python config.
- Use the Supabase anon/public key for the API; reserve service_role for admin tasks.
- See `docs/SETUP-GUIDE.md` for credential setup and safety notes.
