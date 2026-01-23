-- Supabase Database Schema for Slovak Celebrity Gossip Automation System
-- Run this script in your Supabase SQL Editor after creating a new project

-- ============================================================
-- TABLE 1: articles
-- Stores ingested articles (manual uploads or scraping) with scores and format assignments
-- ============================================================

CREATE TABLE IF NOT EXISTS articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
  source_url TEXT NOT NULL UNIQUE,
  source_website TEXT NOT NULL,
  title TEXT,
  raw_html TEXT,
  content TEXT,
  summary TEXT,
  judge_score INTEGER,
  format_assignments JSONB DEFAULT '[]'::jsonb,
  content_hash TEXT,
  duplicate_of UUID REFERENCES articles(id) ON DELETE SET NULL,
  unusable BOOLEAN DEFAULT FALSE,
  unusable_reason TEXT,
  unusable_at TIMESTAMP WITH TIME ZONE,
  processed BOOLEAN DEFAULT FALSE,
  scored BOOLEAN DEFAULT FALSE,
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_articles_processed
  ON articles(processed) WHERE processed = FALSE;

CREATE INDEX IF NOT EXISTS idx_articles_scored
  ON articles(scored) WHERE scored = FALSE;

CREATE INDEX IF NOT EXISTS idx_articles_scraped_at
  ON articles(scraped_at DESC);

CREATE INDEX IF NOT EXISTS idx_articles_source_website
  ON articles(source_website);


-- Comments for documentation
COMMENT ON TABLE articles IS 'Stores ingested content (manual uploads or scraped pages)';
COMMENT ON COLUMN articles.source_url IS 'Original URL or manual identifier (UNIQUE constraint prevents duplicates)';
COMMENT ON COLUMN articles.source_website IS 'Origin tag (manual or website domain)';
COMMENT ON COLUMN articles.raw_html IS 'Raw HTML or extracted text for extraction';
COMMENT ON COLUMN articles.summary IS 'GPT-5 Nano extracted summary (~500 tokens)';
COMMENT ON COLUMN articles.judge_score IS 'First Judge score (1-10, NULL if not scored yet)';
COMMENT ON COLUMN articles.format_assignments IS 'JSONB array of assigned formats: ["headline", "carousel", "video", "podcast"]';
COMMENT ON COLUMN articles.processed IS 'TRUE after extraction (summary generated)';
COMMENT ON COLUMN articles.scored IS 'TRUE after first judge scoring';
COMMENT ON COLUMN articles.content_hash IS 'Hash of normalized article content for dedupe';
COMMENT ON COLUMN articles.duplicate_of IS 'Reference to canonical article when deduped';
COMMENT ON COLUMN articles.unusable IS 'TRUE if content is too old/low score/duplicate';
COMMENT ON COLUMN articles.unusable_reason IS 'Reason for marking unusable';

-- ============================================================
-- TABLE 1A: category_pages
-- Stores category/listing pages for link extraction
-- ============================================================

CREATE TABLE IF NOT EXISTS category_pages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_url TEXT NOT NULL UNIQUE,
  source_website TEXT NOT NULL,
  raw_html TEXT,
  processed BOOLEAN DEFAULT FALSE,
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_category_pages_processed
  ON category_pages(processed) WHERE processed = FALSE;

CREATE INDEX IF NOT EXISTS idx_category_pages_scraped_at
  ON category_pages(scraped_at DESC);

CREATE INDEX IF NOT EXISTS idx_category_pages_source_website
  ON category_pages(source_website);

-- Comments for documentation
COMMENT ON TABLE category_pages IS 'Stores category/listing pages for link extraction';
COMMENT ON COLUMN category_pages.source_url IS 'Category/listing URL (UNIQUE constraint prevents duplicates)';
COMMENT ON COLUMN category_pages.raw_html IS 'Raw HTML content for link extraction';
COMMENT ON COLUMN category_pages.processed IS 'TRUE after links are extracted';

-- ============================================================
-- TABLE 1B: article_urls
-- Stores discovered article URLs for full scraping
-- ============================================================

CREATE TABLE IF NOT EXISTS article_urls (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  article_url TEXT NOT NULL UNIQUE,
  source_website TEXT NOT NULL,
  category_page_id UUID REFERENCES category_pages(id) ON DELETE CASCADE,
  scraped BOOLEAN DEFAULT FALSE,
  discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_article_urls_scraped
  ON article_urls(scraped) WHERE scraped = FALSE;

CREATE INDEX IF NOT EXISTS idx_article_urls_website
  ON article_urls(source_website);

CREATE INDEX IF NOT EXISTS idx_article_urls_discovered_at
  ON article_urls(discovered_at DESC);

-- Comments for documentation
COMMENT ON TABLE article_urls IS 'Stores discovered article URLs pending full scraping';
COMMENT ON COLUMN article_urls.article_url IS 'Unique URL for a full article page';
COMMENT ON COLUMN article_urls.category_page_id IS 'FK to category_pages.id';
COMMENT ON COLUMN article_urls.scraped IS 'TRUE after full article HTML is collected';

-- ============================================================
-- TABLE 2: posts
-- Stores generated content from AI models
-- ============================================================

CREATE TABLE IF NOT EXISTS posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,
  content_type TEXT NOT NULL,
  generating_model TEXT NOT NULL,
  judge_score INTEGER,
  selected BOOLEAN DEFAULT FALSE,
  content JSONB NOT NULL,
  media_urls TEXT[],
  posted BOOLEAN DEFAULT FALSE,
  posted_at TIMESTAMP WITH TIME ZONE,
  post_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_posts_article_id
  ON posts(article_id);

CREATE INDEX IF NOT EXISTS idx_posts_selected
  ON posts(selected) WHERE selected = TRUE;

CREATE INDEX IF NOT EXISTS idx_posts_posted
  ON posts(posted) WHERE posted = FALSE;

CREATE INDEX IF NOT EXISTS idx_posts_platform
  ON posts(platform);

CREATE INDEX IF NOT EXISTS idx_posts_content_type
  ON posts(content_type);

CREATE INDEX IF NOT EXISTS idx_posts_generating_model
  ON posts(generating_model);

-- Comments for documentation
COMMENT ON TABLE posts IS 'Stores AI-generated social media content (3 versions per article per format)';
COMMENT ON COLUMN posts.platform IS 'Target platform: instagram, facebook, tiktok, youtube';
COMMENT ON COLUMN posts.content_type IS 'Format: headline, carousel, video, podcast';
COMMENT ON COLUMN posts.generating_model IS 'AI model: gpt-5-mini, claude-haiku-4.5, gemini-2.5-flash';
COMMENT ON COLUMN posts.judge_score IS 'Second Judge score (NULL until judged)';
COMMENT ON COLUMN posts.selected IS 'TRUE if Second Judge selected this as best version';
COMMENT ON COLUMN posts.content IS 'JSONB content (varies by format - headline text, carousel slides, video script, etc.)';
COMMENT ON COLUMN posts.media_urls IS 'Array of media URLs (images, videos, audio files)';
COMMENT ON COLUMN posts.posted IS 'TRUE after publishing to platform';
COMMENT ON COLUMN posts.post_url IS 'URL of published post (from platform API response)';

-- ============================================================
-- TABLE 3: performance_metrics
-- Stores engagement data at checkpoints
-- ============================================================

CREATE TABLE IF NOT EXISTS performance_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  checkpoint TEXT NOT NULL,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  views INTEGER DEFAULT 0,
  engagement_rate DECIMAL(5,2),
  measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(post_id, checkpoint)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_performance_post_id
  ON performance_metrics(post_id);

CREATE INDEX IF NOT EXISTS idx_performance_checkpoint
  ON performance_metrics(checkpoint);

CREATE INDEX IF NOT EXISTS idx_performance_engagement_rate
  ON performance_metrics(engagement_rate DESC);

-- Comments for documentation
COMMENT ON TABLE performance_metrics IS 'Stores engagement metrics collected at 1hr, 6hr, 24hr checkpoints';
COMMENT ON COLUMN performance_metrics.checkpoint IS 'Checkpoint: 1hr, 6hr, or 24hr';
COMMENT ON COLUMN performance_metrics.engagement_rate IS 'Calculated: (likes + comments*2 + shares*3) / views * 100';
COMMENT ON COLUMN performance_metrics.measured_at IS 'Timestamp when metrics were collected from platform API';

-- ============================================================
-- TABLE 4: model_performance
-- Tracks AI model effectiveness over time
-- ============================================================

CREATE TABLE IF NOT EXISTS model_performance (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_name TEXT NOT NULL,
  content_type TEXT NOT NULL,
  judge_wins INTEGER DEFAULT 0,
  avg_engagement DECIMAL(5,2),
  total_posts INTEGER DEFAULT 0,
  last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(model_name, content_type)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_model_performance_wins
  ON model_performance(judge_wins DESC);

CREATE INDEX IF NOT EXISTS idx_model_performance_engagement
  ON model_performance(avg_engagement DESC);

-- Comments for documentation
COMMENT ON TABLE model_performance IS 'Tracks which AI models win Second Judge selection most often';
COMMENT ON COLUMN model_performance.model_name IS 'AI model: gpt-5-mini, claude-haiku-4.5, gemini-2.5-flash';
COMMENT ON COLUMN model_performance.content_type IS 'Format: headline, carousel, video, podcast';
COMMENT ON COLUMN model_performance.judge_wins IS 'Number of times Second Judge selected this model';
COMMENT ON COLUMN model_performance.avg_engagement IS 'Rolling average engagement rate for posts from this model';
COMMENT ON COLUMN model_performance.total_posts IS 'Total number of posts generated by this model';

-- ============================================================
-- PROJECT MANAGEMENT (V1)
-- ============================================================

-- TABLE 5: projects
-- Groups sources and publishing targets
CREATE TABLE IF NOT EXISTS projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  language TEXT DEFAULT 'en',
  generation_interval_hours INTEGER DEFAULT 12,
  unusable_score_threshold INTEGER DEFAULT 5,
  unusable_age_hours INTEGER DEFAULT 48,
  video_prompt_extra TEXT,
  audio_roundup_prompt_extra TEXT,
  podcast_image_prompt TEXT,
  last_generated_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE projects IS 'User-defined content projects (topics)';
COMMENT ON COLUMN projects.language IS 'Language code for generation (e.g. en, es, sk)';
COMMENT ON COLUMN projects.generation_interval_hours IS 'How often to generate content (hours)';
COMMENT ON COLUMN projects.last_generated_at IS 'Last time generation ran for this project';
COMMENT ON COLUMN projects.unusable_score_threshold IS 'Score below this becomes unusable after age window';
COMMENT ON COLUMN projects.unusable_age_hours IS 'Age window (hours) for low-score content to be unusable';
COMMENT ON COLUMN projects.video_prompt_extra IS 'Extra instructions appended to short-form video prompt';
COMMENT ON COLUMN projects.audio_roundup_prompt_extra IS 'Extra instructions appended to audio roundup prompt';
COMMENT ON COLUMN projects.podcast_image_prompt IS 'Prompt used to generate a single, reusable podcast image per project';

-- TABLE 6: sources
-- RSS feeds, pages, or other source types per project
CREATE TABLE IF NOT EXISTS sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  source_type TEXT NOT NULL,
  url TEXT NOT NULL,
  enabled BOOLEAN DEFAULT TRUE,
  config JSONB DEFAULT '{}'::jsonb,
  scrape_interval_hours INTEGER DEFAULT 6,
  last_scraped_at TIMESTAMP WITH TIME ZONE,
  last_status TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id, url)
);

CREATE INDEX IF NOT EXISTS idx_sources_project_id ON sources(project_id);
CREATE INDEX IF NOT EXISTS idx_sources_enabled ON sources(enabled) WHERE enabled = TRUE;
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(source_type);

COMMENT ON TABLE sources IS 'Per-project content sources (rss, page, reddit, youtube)';
COMMENT ON COLUMN sources.scrape_interval_hours IS 'How often to scrape this source (hours)';

-- TABLE 7: source_items
-- Latest scraped items for monitoring and debugging
CREATE TABLE IF NOT EXISTS source_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
  title TEXT,
  url TEXT NOT NULL,
  content TEXT,
  raw TEXT,
  published_at TIMESTAMP WITH TIME ZONE,
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(source_id, url)
);

CREATE INDEX IF NOT EXISTS idx_source_items_source_id ON source_items(source_id);
CREATE INDEX IF NOT EXISTS idx_source_items_scraped_at ON source_items(scraped_at DESC);

COMMENT ON TABLE source_items IS 'Latest scraped items for each source';

-- TABLE 7A: article_usage
-- Tracks when an article is used in downstream content (e.g., audio roundup)
CREATE TABLE IF NOT EXISTS article_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
  usage_type TEXT NOT NULL,
  post_id UUID REFERENCES posts(id) ON DELETE SET NULL,
  used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_article_usage_article_id ON article_usage(article_id);
CREATE INDEX IF NOT EXISTS idx_article_usage_usage_type ON article_usage(usage_type);

COMMENT ON TABLE article_usage IS 'Tracks usage of articles in downstream content';

-- TABLE 7B: pipeline_runs
-- Tracks per-project pipeline executions for cadence tuning
CREATE TABLE IF NOT EXISTS pipeline_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  run_type TEXT DEFAULT 'pipeline',
  status TEXT DEFAULT 'ok',
  scrape_count INTEGER DEFAULT 0,
  ingest_count INTEGER DEFAULT 0,
  extract_count INTEGER DEFAULT 0,
  judge_count INTEGER DEFAULT 0,
  dedupe_count INTEGER DEFAULT 0,
  unusable_count INTEGER DEFAULT 0,
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  finished_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_project_id ON pipeline_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started_at ON pipeline_runs(started_at DESC);

COMMENT ON TABLE pipeline_runs IS 'Per-project pipeline run metrics (scrape/ingest/extract/judge)';

-- TABLE 8: youtube_accounts
-- Stores OAuth refresh tokens per project (server-side use only)
CREATE TABLE IF NOT EXISTS youtube_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  channel_title TEXT,
  refresh_token TEXT NOT NULL,
  scopes TEXT[] DEFAULT '{}'::text[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id)
);

COMMENT ON TABLE youtube_accounts IS 'OAuth refresh tokens for YouTube uploads';

-- TABLE 9: youtube_metrics
-- Stores daily YouTube Analytics metrics per project
CREATE TABLE IF NOT EXISTS youtube_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  channel_id TEXT,
  channel_title TEXT,
  report_date DATE NOT NULL,
  views INTEGER,
  watch_time_minutes NUMERIC,
  average_view_duration_seconds NUMERIC,
  likes INTEGER,
  comments INTEGER,
  subscribers_gained INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(project_id, report_date)
);

CREATE INDEX IF NOT EXISTS idx_youtube_metrics_project_id ON youtube_metrics(project_id);
CREATE INDEX IF NOT EXISTS idx_youtube_metrics_report_date ON youtube_metrics(report_date DESC);

COMMENT ON TABLE youtube_metrics IS 'Daily YouTube Analytics metrics per project';
COMMENT ON COLUMN youtube_metrics.report_date IS 'UTC date of the analytics report';
COMMENT ON COLUMN youtube_metrics.watch_time_minutes IS 'Total minutes watched';
COMMENT ON COLUMN youtube_metrics.average_view_duration_seconds IS 'Average view duration in seconds';

-- TABLE 10: youtube_video_metrics
-- Stores per-video checkpoint metrics for A/B testing
CREATE TABLE IF NOT EXISTS youtube_video_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  video_id TEXT NOT NULL,
  checkpoint TEXT NOT NULL,
  views INTEGER,
  likes INTEGER,
  comments INTEGER,
  watch_time_minutes NUMERIC,
  average_view_duration_seconds NUMERIC,
  collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(post_id, checkpoint)
);

CREATE INDEX IF NOT EXISTS idx_youtube_video_metrics_project_id ON youtube_video_metrics(project_id);
CREATE INDEX IF NOT EXISTS idx_youtube_video_metrics_post_id ON youtube_video_metrics(post_id);
CREATE INDEX IF NOT EXISTS idx_youtube_video_metrics_checkpoint ON youtube_video_metrics(checkpoint);

COMMENT ON TABLE youtube_video_metrics IS 'Per-video checkpoint metrics (views/likes/comments + watch time)';
COMMENT ON COLUMN youtube_video_metrics.checkpoint IS 'Checkpoint label (1h, 12h, 24h, 3d, 7d, 14d, 30d)';

-- ============================================================
-- TABLE 11: tts_rotation
-- Atomic counter for rotating TTS voice pairs
-- ============================================================

CREATE TABLE IF NOT EXISTS tts_rotation (
  id INTEGER PRIMARY KEY DEFAULT 1,
  counter INTEGER NOT NULL DEFAULT 0,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE tts_rotation IS 'Global counter for rotating TTS voice combinations';

-- ============================================================
-- MIGRATION HELPERS (safe to re-run)
-- ============================================================

ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'en';

ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS generation_interval_hours INTEGER DEFAULT 12;

ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS unusable_score_threshold INTEGER DEFAULT 5;

ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS unusable_age_hours INTEGER DEFAULT 48;

ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS video_prompt_extra TEXT;

ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS audio_roundup_prompt_extra TEXT;

ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS podcast_image_prompt TEXT;

-- Ensure rotation row exists for TTS combos
INSERT INTO tts_rotation (id, counter)
VALUES (1, 0)
ON CONFLICT (id) DO NOTHING;

ALTER TABLE IF EXISTS articles
  ADD COLUMN IF NOT EXISTS project_id UUID REFERENCES projects(id) ON DELETE SET NULL;

ALTER TABLE IF EXISTS articles
  ADD COLUMN IF NOT EXISTS content_hash TEXT;

ALTER TABLE IF EXISTS articles
  ADD COLUMN IF NOT EXISTS source_id UUID REFERENCES sources(id) ON DELETE SET NULL;

ALTER TABLE IF EXISTS articles
  ADD COLUMN IF NOT EXISTS duplicate_of UUID REFERENCES articles(id) ON DELETE SET NULL;

ALTER TABLE IF EXISTS articles
  ADD COLUMN IF NOT EXISTS unusable BOOLEAN DEFAULT FALSE;

ALTER TABLE IF EXISTS articles
  ADD COLUMN IF NOT EXISTS unusable_reason TEXT;

ALTER TABLE IF EXISTS articles
  ADD COLUMN IF NOT EXISTS unusable_at TIMESTAMP WITH TIME ZONE;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'articles' AND column_name = 'project_id'
  ) THEN
    CREATE INDEX IF NOT EXISTS idx_articles_project_id ON articles(project_id);
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'articles' AND column_name = 'source_id'
  ) THEN
    CREATE INDEX IF NOT EXISTS idx_articles_source_id ON articles(source_id);
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'articles' AND column_name = 'content_hash'
  ) THEN
    CREATE INDEX IF NOT EXISTS idx_articles_content_hash ON articles(content_hash);
  END IF;
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'articles' AND column_name = 'unusable'
  ) THEN
    CREATE INDEX IF NOT EXISTS idx_articles_unusable ON articles(unusable) WHERE unusable = TRUE;
  END IF;
END $$;

ALTER TABLE IF EXISTS projects
  ADD COLUMN IF NOT EXISTS last_generated_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE IF EXISTS sources
  ADD COLUMN IF NOT EXISTS scrape_interval_hours INTEGER DEFAULT 6;

-- ============================================================
-- HELPER VIEWS (Optional but useful)
-- ============================================================

-- View: Unprocessed articles queue
CREATE OR REPLACE VIEW unprocessed_articles AS
SELECT
  id,
  source_website,
  title,
  scraped_at,
  EXTRACT(EPOCH FROM (NOW() - scraped_at))/3600 AS hours_waiting
FROM articles
WHERE processed = FALSE
ORDER BY scraped_at ASC;

COMMENT ON VIEW unprocessed_articles IS 'Articles waiting for extraction (processed = FALSE)';

-- View: Unscored articles queue
CREATE OR REPLACE VIEW unscored_articles AS
SELECT
  id,
  source_website,
  title,
  summary,
  scraped_at,
  EXTRACT(EPOCH FROM (NOW() - scraped_at))/3600 AS hours_waiting
FROM articles
WHERE processed = TRUE AND scored = FALSE
ORDER BY scraped_at ASC;

COMMENT ON VIEW unscored_articles IS 'Articles waiting for First Judge scoring (processed = TRUE, scored = FALSE)';

-- View: Publishing queue
CREATE OR REPLACE VIEW publishing_queue AS
SELECT
  p.id,
  p.platform,
  p.content_type,
  p.generating_model,
  p.selected,
  a.title AS article_title,
  a.source_website,
  a.judge_score AS article_score,
  p.created_at
FROM posts p
JOIN articles a ON p.article_id = a.id
WHERE p.selected = TRUE AND p.posted = FALSE
ORDER BY a.judge_score DESC, p.created_at ASC;

COMMENT ON VIEW publishing_queue IS 'Selected posts waiting to be published (selected = TRUE, posted = FALSE)';

-- View: Model leaderboard
CREATE OR REPLACE VIEW model_leaderboard AS
SELECT
  model_name,
  content_type,
  judge_wins,
  avg_engagement,
  total_posts,
  ROUND((judge_wins::DECIMAL / NULLIF(total_posts, 0)) * 100, 2) AS win_rate_percent
FROM model_performance
ORDER BY content_type, judge_wins DESC;

COMMENT ON VIEW model_leaderboard IS 'AI model performance leaderboard by format';

-- ============================================================
-- HELPER FUNCTIONS (Optional but useful)
-- ============================================================

-- Function: Get queue size (for dynamic threshold in First Judge)
CREATE OR REPLACE FUNCTION get_queue_size()
RETURNS INTEGER AS $$
BEGIN
  RETURN (
    SELECT COUNT(*)
    FROM posts
    WHERE selected = TRUE AND posted = FALSE
  );
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_queue_size IS 'Returns number of posts waiting to be published (for dynamic threshold)';

-- Function: Update model performance (call after Second Judge selection)
CREATE OR REPLACE FUNCTION update_model_performance(
  p_model_name TEXT,
  p_content_type TEXT,
  p_is_winner BOOLEAN
)
RETURNS VOID AS $$
BEGIN
  INSERT INTO model_performance (model_name, content_type, judge_wins, total_posts)
  VALUES (p_model_name, p_content_type, CASE WHEN p_is_winner THEN 1 ELSE 0 END, 1)
  ON CONFLICT (model_name, content_type)
  DO UPDATE SET
    judge_wins = model_performance.judge_wins + CASE WHEN p_is_winner THEN 1 ELSE 0 END,
    total_posts = model_performance.total_posts + 1,
    last_updated = NOW();
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_model_performance IS 'Increments judge_wins and total_posts for a model after Second Judge selection';

-- Function: Next TTS combo index (atomic)
CREATE OR REPLACE FUNCTION next_tts_combo(p_mod INTEGER DEFAULT 9)
RETURNS INTEGER AS $$
DECLARE current_val INTEGER;
BEGIN
  INSERT INTO tts_rotation (id, counter)
  VALUES (1, 0)
  ON CONFLICT (id) DO NOTHING;

  SELECT counter INTO current_val
  FROM tts_rotation
  WHERE id = 1
  FOR UPDATE;

  UPDATE tts_rotation
  SET counter = counter + 1,
      updated_at = NOW()
  WHERE id = 1;

  RETURN MOD(current_val, p_mod);
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION next_tts_combo IS 'Atomically increments TTS rotation counter and returns index modulo p_mod';

-- ============================================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================================

-- Uncomment to insert sample test data

/*
-- Sample article
INSERT INTO articles (source_url, source_website, title, summary, judge_score, format_assignments, processed, scored)
VALUES (
  'https://www.topky.sk/test-article-1',
  'topky.sk',
  'Test Celebrity News',
  'This is a test summary for a celebrity news article.',
  8,
  '["headline", "carousel", "video", "podcast"]'::jsonb,
  TRUE,
  TRUE
);

-- Sample posts (3 models)
INSERT INTO posts (article_id, platform, content_type, generating_model, content, selected)
SELECT
  id,
  'instagram',
  'headline',
  'gpt-5-mini',
  '{"text": "Test headline from GPT-5 Mini 🔥"}'::jsonb,
  FALSE
FROM articles WHERE source_url = 'https://www.topky.sk/test-article-1';

INSERT INTO posts (article_id, platform, content_type, generating_model, content, selected)
SELECT
  id,
  'instagram',
  'headline',
  'claude-haiku-4.5',
  '{"text": "Test headline from Claude Haiku 4.5 ✨"}'::jsonb,
  TRUE
FROM articles WHERE source_url = 'https://www.topky.sk/test-article-1';

INSERT INTO posts (article_id, platform, content_type, generating_model, content, selected)
SELECT
  id,
  'instagram',
  'headline',
  'gemini-2.5-flash',
  '{"text": "Test headline from Gemini 2.5 Flash 💫"}'::jsonb,
  FALSE
FROM articles WHERE source_url = 'https://www.topky.sk/test-article-1';

-- Sample model performance
INSERT INTO model_performance (model_name, content_type, judge_wins, avg_engagement, total_posts)
VALUES
  ('gpt-5-mini', 'headline', 10, 3.50, 30),
  ('claude-haiku-4.5', 'headline', 15, 4.20, 30),
  ('gemini-2.5-flash', 'headline', 5, 2.80, 30);
*/

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- After running this script, verify the schema with:
/*
-- Check tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Check views exist
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check functions exist
SELECT routine_name
FROM information_schema.routines
WHERE routine_schema = 'public'
ORDER BY routine_name;

-- Check indexes exist
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
*/

-- ============================================================
-- CLEANUP (Optional - for resetting database)
-- ============================================================

-- Uncomment to drop all objects (WARNING: Deletes all data!)
/*
DROP VIEW IF EXISTS unprocessed_articles;
DROP VIEW IF EXISTS unscored_articles;
DROP VIEW IF EXISTS publishing_queue;
DROP VIEW IF EXISTS model_leaderboard;

DROP FUNCTION IF EXISTS get_queue_size();
DROP FUNCTION IF EXISTS update_model_performance(TEXT, TEXT, BOOLEAN);

DROP TABLE IF EXISTS performance_metrics CASCADE;
DROP TABLE IF EXISTS model_performance CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS article_urls CASCADE;
DROP TABLE IF EXISTS category_pages CASCADE;
DROP TABLE IF EXISTS articles CASCADE;
*/

-- ============================================================
-- NOTES
-- ============================================================

/*
After running this schema:

1. Verify tables exist in Supabase dashboard (Database → Tables)
2. Get your Supabase credentials:
   - Go to Settings → API
   - Copy "Project URL" (SUPABASE_URL)
   - Copy "anon public" key (SUPABASE_KEY)
3. Add credentials to .env.local:
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_anon_key
4. Test connection from n8n (create Supabase credential)

Key Design Decisions:
- UUID primary keys (better for distributed systems)
- JSONB for flexible content storage (different formats have different structures)
- ON DELETE CASCADE (delete posts/metrics when article deleted)
- UNIQUE constraints (prevent duplicates: source_url, post_id+checkpoint, model_name+content_type)
- Indexes on frequently queried columns (processed, scored, selected, posted)
- Helper views for common queries (queue sizes, leaderboards)
- Helper functions for workflow logic (queue size, model performance updates)

Performance Considerations:
- Indexes on boolean columns with WHERE clauses (processed = FALSE, etc.)
- JSONB for content (faster than TEXT with JSON parsing)
- Timestamps with timezone (UTC standardization)
- Partial indexes (only index rows WHERE condition is TRUE)

Cost Optimization:
- Supabase free tier: 500 MB database, 1 GB file storage
- Estimated storage: ~100 MB per 10,000 articles
- Monitor with: SELECT pg_size_pretty(pg_database_size('postgres'));
*/
