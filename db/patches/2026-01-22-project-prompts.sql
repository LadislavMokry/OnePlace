ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS video_prompt_extra TEXT;

ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS audio_roundup_prompt_extra TEXT;
