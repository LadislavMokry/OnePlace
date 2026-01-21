-- Add youtube_metrics table for daily analytics
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
