# Repository Guidelines

## Project Structure & Module Organization
This repo is an n8n workflow automation project with supporting specs and database schema.

- Workflow exports (JSON): `workflows/scraper-hourly-collection.json`, `workflows/link-extractor.json`, `workflows/cleanup-raw-html.json`, `workflows/test-supabase-connection.json`.
- Database schema: `db/supabase-schema.sql` (tables for articles, posts, metrics).
- Guides and specs: `docs/SETUP-GUIDE.md`, `docs/scraper-workflow-quick-start.md`, `docs/slovak-gossip-automation-spec (1).md`, `docs/implementation-plan.md`, `docs/todo.md`.
- Agent/n8n guidance: `CLAUDE.md` and `n8n-skills/` (reference only).

## Build, Test, and Development Commands
There is no build step or test runner in this repo; workflows are executed in the n8n UI.

- Install tooling (optional): `npm install` (installs the Supabase CLI dependency).
- Run n8n locally via your existing setup (e.g., `n8n start`) and open `http://localhost:5678`.
- Apply schema by running `db/supabase-schema.sql` in the Supabase SQL Editor.
- Import workflow JSON files in n8n (Workflows -> Import from File).

## Coding Style & Naming Conventions
- JSON files use 2-space indentation; keep exports consistent.
- Workflow files use kebab-case names (example: `workflows/scraper-hourly-collection.json`).
- Workflow names follow `Module - Purpose` (example: `Scraper - Hourly Data Collection`).
- Node names should be explicit (example: `HTTP Request - Topky`, `IF - Check Status`).
- Supabase nodes must use explicit field mapping (`dataMode: defineBelow`); avoid auto-mapping.

## Testing Guidelines
- Use `workflows/test-supabase-connection.json` to validate Supabase connectivity end-to-end.
- Prefer Manual Trigger + Execute Workflow runs in n8n for verification.
- Validate data with SQL queries in the Supabase dashboard (see `docs/scraper-workflow-quick-start.md`).

## Commit & Pull Request Guidelines
- History uses short, sentence-style messages without a strict convention.
- Keep commits scoped and descriptive (example: `Fix Supabase Get nodes: add returnAll parameter`).
- PRs should include: summary, exported workflow JSON, schema changes (if any), and test notes.
- Add screenshots of updated workflow canvases when behavior changes.

## Security & Configuration Tips
- Store secrets in `.env.local`; never commit API keys.
- Use the Supabase anon/public key for n8n workflows; reserve service_role for admin tasks.
- See `docs/SETUP-GUIDE.md` for credential setup and safety notes.
