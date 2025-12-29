-- Supabase Database Schema for Slovak Celebrity Gossip Automation System
-- Run this script in your Supabase SQL Editor after creating a new project

-- ============================================================
-- TABLE 1: articles
-- Stores scraped articles with scores and format assignments
-- ============================================================

CREATE TABLE IF NOT EXISTS articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_url TEXT NOT NULL UNIQUE,
  source_website TEXT NOT NULL,
  title TEXT,
  raw_html TEXT,
  content TEXT,
  summary TEXT,
  judge_score INTEGER,
  format_assignments JSONB DEFAULT '[]'::jsonb,
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
COMMENT ON TABLE articles IS 'Stores scraped celebrity news articles from Slovak websites';
COMMENT ON COLUMN articles.source_url IS 'Original article URL (UNIQUE constraint prevents duplicates)';
COMMENT ON COLUMN articles.source_website IS 'Website name (topky.sk, cas.sk, pluska.sk, refresher.sk, startitup.sk)';
COMMENT ON COLUMN articles.raw_html IS 'Raw HTML content (50k-100k tokens) for extraction';
COMMENT ON COLUMN articles.summary IS 'GPT-5 Nano extracted summary (~500 tokens)';
COMMENT ON COLUMN articles.judge_score IS 'First Judge score (1-10, NULL if not scored yet)';
COMMENT ON COLUMN articles.format_assignments IS 'JSONB array of assigned formats: ["headline", "carousel", "video", "podcast"]';
COMMENT ON COLUMN articles.processed IS 'TRUE after extraction (summary generated)';
COMMENT ON COLUMN articles.scored IS 'TRUE after first judge scoring';

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
