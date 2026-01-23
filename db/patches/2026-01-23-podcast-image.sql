ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS podcast_image_prompt TEXT;
