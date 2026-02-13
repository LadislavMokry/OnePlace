# Podcast Relaunch Todo
Date: 2026-02-13

## Topic Suggestions (Women-Focused)
- Relationships and dating
- Mental health and psychology
- Beauty and skincare
- Parenting and family
- Home and organization
- Career and workplace
- Wellness and fitness
- Fashion and style

## 1. Product Decisions
- Finalize podcast topics and names.
- Define tagline per podcast.
- Define the one-sentence standardized intro per podcast.
- Choose additional women-focused topic(s).
- Decide target story count per episode for 12–15 minutes.

## 2. Projects and Sources
- Update projects to the new topic set.
- Remove old projects and sources.
- Build source lists per topic (RSS, Reddit, YouTube feeds, pages).
- Create or update RSS buckets per project.
- Seed sources via Admin UI or script.

## 3. Audio Length and Structure
- Adjust audio roundup prompt to target 12–15 minutes.
- Set story count and token budget to match 12–15 minutes.
- Add per-story jingle insertion in the audio rendering pipeline.
- Track story-to-audio segment mapping to insert jingles reliably.

## 4. RSS Duration Accuracy
- Compute actual audio duration from the MP3 file.
- Write actual duration into RSS (not hardcoded).
- Backfill existing episodes in RSS if needed.

## 5. Publishing Profiles and Artwork
- Create one YouTube channel per podcast.
- Create podcast app profiles (Apple/Spotify) per podcast.
- Generate YouTube thumbnail (16:9 for podcast video).
- Generate podcast square artwork (1:1).
- Include title, tagline, and logo placeholder in both images.
- Ensure RSS per project uses the correct artwork and metadata.

## 6. YouTube Upload
- Upload each episode to its matching YouTube channel.
- Add per-project YouTube OAuth tokens.
- Verify scheduled publishing for all projects.

## 7. Metrics to /stats
- Implement Spotify podcast metrics ingestion.
- Implement Apple Podcasts metrics ingestion.
- Store metrics in Supabase.
- Expose metrics on the /stats UI.

## 8. LLM Provider A/B
- Add multiple script models/providers.
- Store provider and model per episode in the database.
- Track performance metrics per model.

## Open Questions
- Final topic list and names (including women-focused topics).
- Target stories per episode (8, 10, or 12) to hit 12–15 minutes.
- Jingle audio file available, or generate a placeholder?
- LLM providers to compare (OpenAI, Anthropic, Google, others).
- Apple/Spotify accounts and YouTube channels already created?
