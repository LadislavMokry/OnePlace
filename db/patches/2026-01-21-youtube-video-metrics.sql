-- Add youtube_video_metrics table for per-video checkpoint analytics
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
