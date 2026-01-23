# Today TODO (2026-01-23)

## Step 1: Longer podcasts (10-15 min) + more topics
- [x] Update audio roundup prompt to 10-15 minutes and raise max tokens.
- [x] Increase default `AUDIO_ROUNDUP_SIZE` to 8 (configurable via env).
- [ ] Decide target stories per project (ex: 8-10) and set `AUDIO_ROUNDUP_SIZE` in `.env.local` on server.
- [ ] Run a manual audio roundup to validate length and pacing.

## Step 2: YouTube channels (4 new channels)
- [ ] Create 4 additional YouTube channels (one per remaining project topic).
- [ ] Run OAuth per channel and store refresh tokens in `youtube_accounts`.
- [ ] Verify upload flow: `python -m app.worker youtube-upload --all-projects`.
- [ ] Confirm daily systemd timer covers all projects and posts correctly.

## Step 3: Podcasts (Spotify + Apple)
- [ ] Create creator accounts: Spotify for Podcasters + Apple Podcasts Connect.
- [ ] Create 5 shows (one per project) with the new static artwork.
- [ ] Decide hosting/automation path (direct API vs. RSS hosting provider).
- [ ] Implement automated publishing once provider/API is confirmed.

## Step 4: Project-wide podcast images (single image per project)
- [x] Add `projects.podcast_image_prompt` and Admin UI field.
- [x] Add reusable project image generation + use it for roundup thumbnails.
- [ ] Fill prompts for each project in Admin UI.
- [ ] Generate images:
  - `python -m app.worker podcast-image --all-projects`
- [ ] Re-render latest roundup videos to confirm project images are used.

## Step 5: Profile pictures
- [ ] Use the project podcast images as YouTube channel icons (or generate variants).
- [ ] Export in square size (YouTube: 800x800+; Spotify/Apple: 3000x3000 requirement; upscale if needed).
