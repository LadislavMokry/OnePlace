# Slovak Celebrity Gossip Content Automation - Implementation Plan

## Project Overview

This is the implementation roadmap for building a Slovak Celebrity Gossip Content Automation System using n8n workflow automation. The system scrapes Slovak celebrity news, generates multi-format social media content using AI, and publishes to Instagram, Facebook, TikTok, and YouTube.

**Target Platform**: n8n workflow automation (local instance at http://localhost:5678)
**Content Language**: Slovak
**Architecture**: Modular sub-workflow pipeline with 9 main components
**Cost Target**: ~$4.30/day for AI/ML operations

---

## Development Approach: Modular Sub-Workflow Architecture

### Why Modular?
- 9 distinct components with clear boundaries
- Easier testing, debugging, and iteration
- Independent deployment and validation
- Matches n8n best practices (use "Execute Workflow" nodes)
- Average 56 seconds between edits suggests incremental development works best

### Architecture Overview

```
Main Orchestrator Workflow
├─ Sub-workflow 1A: Data Collection (hourly scraping - 5 Slovak sites) ✅
├─ Sub-workflow 1B: Link Extraction (extract article URLs from category pages)
├─ Sub-workflow 1C: Article Scraping (fetch individual article content)
├─ Sub-workflow 2: Extraction (GPT-5 Nano summarization)
├─ Sub-workflow 3: First Judge (scoring 1-10, format assignment)
├─ Sub-workflow 4: Content Generation (3 models in parallel)
├─ Sub-workflow 5: Second Judge (best version selection)
├─ Sub-workflow 6A: Media Creation - Images
├─ Sub-workflow 6B: Media Creation - Videos
├─ Sub-workflow 6C: Media Creation - Podcasts
├─ Sub-workflow 7: Publishing (rate-limited, 6 windows/day)
└─ Sub-workflow 8: Performance Tracking (1hr/6hr/24hr checkpoints)
```

---

## Phase 0: Initial Setup

### Status: In Progress

### 1. Supabase Database Setup

**Action Items**:
- [ ] Create Supabase account (https://supabase.com)
- [ ] Create new project (select closest region to Slovakia)
- [ ] Run database schema SQL (see below)
- [ ] Get `SUPABASE_URL` and `SUPABASE_KEY` from Settings → API
- [ ] Test connection from n8n

**Database Schema** (4 tables):

#### Table 1: `articles`
Stores scraped articles with scores and format assignments.

```sql
CREATE TABLE articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_url TEXT NOT NULL UNIQUE,
  source_website TEXT NOT NULL,
  title TEXT,
  raw_html TEXT,
  content TEXT,
  summary TEXT,
  judge_score INTEGER,
  format_assignments JSONB,
  processed BOOLEAN DEFAULT FALSE,
  scored BOOLEAN DEFAULT FALSE,
  scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_articles_processed ON articles(processed) WHERE processed = FALSE;
CREATE INDEX idx_articles_scored ON articles(scored) WHERE scored = FALSE;
CREATE INDEX idx_articles_scraped_at ON articles(scraped_at DESC);
```

#### Table 2: `posts`
Stores generated content from AI models.

```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
  platform TEXT NOT NULL, -- 'instagram', 'facebook', 'tiktok', 'youtube'
  content_type TEXT NOT NULL, -- 'headline', 'carousel', 'video', 'podcast'
  generating_model TEXT NOT NULL, -- 'gpt-5-mini', 'claude-haiku-4.5', 'gemini-2.5-flash'
  judge_score INTEGER,
  selected BOOLEAN DEFAULT FALSE,
  content JSONB NOT NULL,
  media_urls TEXT[],
  posted BOOLEAN DEFAULT FALSE,
  posted_at TIMESTAMP WITH TIME ZONE,
  post_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_posts_article_id ON posts(article_id);
CREATE INDEX idx_posts_selected ON posts(selected) WHERE selected = TRUE;
CREATE INDEX idx_posts_posted ON posts(posted) WHERE posted = FALSE;
```

#### Table 3: `performance_metrics`
Stores engagement data at checkpoints.

```sql
CREATE TABLE performance_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
  checkpoint TEXT NOT NULL, -- '1hr', '6hr', '24hr'
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  views INTEGER DEFAULT 0,
  engagement_rate DECIMAL(5,2),
  measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(post_id, checkpoint)
);

CREATE INDEX idx_performance_post_id ON performance_metrics(post_id);
```

#### Table 4: `model_performance`
Tracks AI model effectiveness over time.

```sql
CREATE TABLE model_performance (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_name TEXT NOT NULL,
  content_type TEXT NOT NULL,
  judge_wins INTEGER DEFAULT 0,
  avg_engagement DECIMAL(5,2),
  total_posts INTEGER DEFAULT 0,
  last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(model_name, content_type)
);

CREATE INDEX idx_model_performance_wins ON model_performance(judge_wins DESC);
```

### 2. API Keys Setup

**Immediate Need** (Phase 1):
- [ ] `OPENAI_API_KEY` - For GPT-5 Nano extraction and judging
- [ ] `SUPABASE_URL` - Supabase project URL
- [ ] `SUPABASE_KEY` - Supabase anon/public key

**Later Phases**:
- [ ] `ANTHROPIC_API_KEY` - Claude Haiku 4.5 (Phase 2)
- [ ] `GOOGLE_AI_API_KEY` - Gemini 2.5 Flash (Phase 2)
- [ ] `ELEVENLABS_API_KEY` - Text-to-speech (Phase 3)
- [ ] `FB_PAGE_ACCESS_TOKEN` - Facebook posting (Phase 4)
- [ ] `INSTAGRAM_ACCOUNT_ID` - Instagram posting (Phase 4)
- [ ] `YOUTUBE_CLIENT_ID` - YouTube posting (Phase 4)
- [ ] `YOUTUBE_CLIENT_SECRET` - YouTube posting (Phase 4)
- [ ] `DISCORD_WEBHOOK_URL` - Error notifications (Optional)

**Update .env.local**:
```bash
# Existing
N8N_API_KEY=your_n8n_key

# Add Phase 1 Keys
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
OPENAI_API_KEY=sk-...
```

### 3. n8n MCP Configuration

**Verify MCP Connection**:
- [ ] Test n8n-mcp tools are available
- [ ] Confirm n8n instance at http://localhost:5678
- [ ] Verify n8n-skills are loaded

---

## Phase 1: Data Collection Pipeline (Week 1)

### Status: In Progress (1A Complete)

### Sub-Workflow 1A: "Scraper - Hourly Data Collection" ✅ COMPLETED

**Purpose**: Scrapes 5 Slovak celebrity news CATEGORY PAGES every hour

**What It Does**:
- Fetches category/listing pages (e.g., topky.sk/se/15/Prominenti)
- These pages contain LINKS to individual articles, not full article content
- Stores category page HTML in Supabase articles table

**Nodes**:
1. **Schedule Trigger** - Cron: `0 * * * *` (every hour)
2. **HTTP Request** (5 parallel branches):
   - topky.sk/se/15/Prominenti
   - cas.sk/r/prominenti
   - pluska.sk/r/soubiznis
   - refresher.sk/osobnosti
   - startitup.sk/kategoria/kultura/
3. **Set Node** (per source) - Format data with source_url, source_website, raw_html
4. **Supabase Insert** - Store raw HTML
5. **Error Handler** - Continue on individual source failure (onError: continueRegularOutput)

**File Location**: `workflows/scraper-hourly-collection.json`

**API Keys Required**: `SUPABASE_URL`, `SUPABASE_KEY` ✅

**Success Criteria**:
- [x] Executes every hour automatically
- [x] Stores HTML from at least 3/5 sources
- [x] Continues on individual failures
- [x] No duplicate URLs stored

---

### Sub-Workflow 1B: "Link Extractor - Article URL Discovery"

**Purpose**: Extracts individual article URLs from category page HTML

**What It Does**:
- Reads category HTML from articles table (where raw_html contains links)
- Extracts URLs of individual articles using regex/parsing
- Stores unique article URLs (deduplication)
- Marks category pages as processed

**Input**: Category page HTML from Sub-Workflow 1A
**Output**: Table of article URLs to scrape

**Nodes**:
1. **Schedule Trigger** - Every 15 minutes (runs after 1A completes)
2. **Supabase Query** - Get category pages (`processed = FALSE`, filter by source_url pattern)
3. **Code Node (JavaScript)** - Extract article URLs:
```javascript
const items = $input.all();
const results = [];

for (const item of items) {
  const html = item.json.raw_html;
  const source_website = item.json.source_website;

  // URL patterns per website
  const patterns = {
    'topky.sk': /<a[^>]+href="(https:\/\/www\.topky\.sk\/clanok\/\d+\/[^"]+)"/gi,
    'cas.sk': /<a[^>]+href="(https:\/\/www\.cas\.sk\/clanok\/\d+\/[^"]+)"/gi,
    'pluska.sk': /<a[^>]+href="(https:\/\/www\d*\.pluska\.sk\/[^"]+)"/gi,
    'refresher.sk': /<a[^>]+href="(https:\/\/refresher\.sk\/\d+\/[^"]+)"/gi,
    'startitup.sk': /<a[^>]+href="(https:\/\/www\.startitup\.sk\/[^"]+)"/gi
  };

  const regex = patterns[source_website];
  if (!regex) continue;

  const urls = [...html.matchAll(regex)].map(match => match[1]);
  const uniqueUrls = [...new Set(urls)]; // Deduplicate

  for (const url of uniqueUrls) {
    results.push({
      json: {
        article_url: url,
        source_website: source_website,
        category_page_id: item.json.id,
        discovered_at: new Date().toISOString()
      }
    });
  }
}

return results;
```
4. **Supabase Insert** - Store article URLs (table: `article_urls` with UNIQUE constraint)
5. **Supabase Update** - Mark category page as `processed = TRUE`

**Database Schema Addition**:
```sql
CREATE TABLE article_urls (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  article_url TEXT NOT NULL UNIQUE,
  source_website TEXT NOT NULL,
  category_page_id UUID REFERENCES articles(id) ON DELETE CASCADE,
  scraped BOOLEAN DEFAULT FALSE,
  discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_article_urls_scraped ON article_urls(scraped) WHERE scraped = FALSE;
CREATE INDEX idx_article_urls_website ON article_urls(source_website);
```

**API Keys Required**: `SUPABASE_URL`, `SUPABASE_KEY`

**Testing Strategy**:
- Test with 1-2 category pages first
- Verify URL regex patterns capture article links
- Check deduplication works (UNIQUE constraint prevents duplicates)
- Confirm category pages marked as processed

**Success Criteria**:
- [ ] Extracts article URLs from category HTML
- [ ] Deduplicates URLs correctly
- [ ] Stores 10-30 article URLs per category page
- [ ] Marks category pages as processed
- [ ] No errors on malformed HTML

---

### Sub-Workflow 1C: "Article Scraper - Full Content Collection"

**Purpose**: Fetches full HTML of individual articles for content extraction

**What It Does**:
- Reads article URLs from `article_urls` table
- Fetches complete article pages (these contain the full story)
- Stores article HTML in `articles` table for extraction
- Marks URLs as scraped

**Input**: Article URLs from Sub-Workflow 1B
**Output**: Full article HTML ready for GPT-5 Nano extraction

**Nodes**:
1. **Schedule Trigger** - Every 10 minutes
2. **Supabase Query** - Get unscraped article URLs (`scraped = FALSE`, LIMIT 20)
3. **SplitInBatches** - Batch size: 10 (parallel fetching)
4. **HTTP Request Node** - Fetch article page:
   - Method: GET
   - URL: `{{ $json.article_url }}`
   - Headers:
     - User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
     - Accept: text/html
     - Accept-Language: sk-SK,sk;q=0.9
   - Timeout: 30000ms
   - Options: neverError: true, includeHeadersAndStatus: true
5. **IF Node** - Check HTTP status = 200
6. **Set Node** - Format for database:
```javascript
{
  source_url: $json.article_url,
  source_website: $json.source_website,
  raw_html: $json.data,
  scraped_at: $now
}
```
7. **Supabase Insert** - Store in `articles` table
8. **Supabase Update** - Mark URL as `scraped = TRUE` in `article_urls` table

**API Keys Required**: `SUPABASE_URL`, `SUPABASE_KEY`

**Testing Strategy**:
- Test with 5-10 article URLs first
- Verify complete article HTML captured
- Check error handling for 404/timeout
- Confirm article content (not just headers/navigation)

**Success Criteria**:
- [ ] Fetches 20 articles every 10 minutes (120/hour max)
- [ ] Stores full article HTML (50k-100k tokens)
- [ ] Handles failed requests gracefully
- [ ] Marks URLs as scraped to prevent re-fetching

---

### Sub-Workflow 2: "Extraction - HTML to Summary"

**Purpose**: Converts raw article HTML (50k-100k tokens) to summaries (~500 tokens) using GPT-5 Nano

**What It Does**:
- Reads full article HTML from Sub-Workflow 1C
- Uses GPT-5 Nano to extract title, content, key people
- Reduces token count by ~98% for downstream processing
- Prepares articles for First Judge

**Input**: Full article HTML from `articles` table
**Output**: Clean article summaries ready for judging

**Nodes**:
1. **Schedule Trigger** - Every 10 minutes
2. **Supabase Query** - Get unprocessed articles (`processed = FALSE`, `raw_html IS NOT NULL`)
3. **SplitInBatches** - Batch size: 10-20
4. **OpenAI Node** (GPT-5 Nano):
   - **System Prompt**: "Extract celebrity news from Slovak HTML. Return JSON: {title, content, key_names}"
   - **Enable Prompt Caching**: Yes (90% savings)
   - **Temperature**: 0.1 (extraction task)
   - **Max Tokens**: 600
   - **Response Format**: JSON Object
5. **Supabase Update** - Store summary, mark `processed = TRUE`

**API Keys Required**: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`

**Testing Strategy**:
- Test with 5-10 sample articles first
- Measure token usage (should be ~500 tokens per article)
- Verify prompt caching is enabled (check OpenAI dashboard)
- Check summary quality (readable Slovak, key info preserved)

**Success Criteria**:
- [ ] Processes unprocessed articles every 10 minutes
- [ ] Reduces 50k-100k tokens to ~500 tokens
- [ ] Prompt caching saves 90% on repeated system prompts
- [ ] Cost: ~$0.0001 per article (GPT-5 Nano pricing)

---

### Sub-Workflow 3: "First Judge - Scoring & Format Assignment"

**Purpose**: Scores articles 1-10, assigns content formats based on quality and queue size

**Nodes**:
1. **Schedule Trigger** - Every 15 minutes
2. **Supabase Query** - Get unscored articles (`scored = FALSE`)
3. **Supabase Query** - Get queue size (count unposted content)
4. **Code Node** - Calculate dynamic threshold:
```javascript
const queueSize = $json.queue_size;
let minScore = 4;
if (queueSize >= 60) minScore = 7;
else if (queueSize >= 40) minScore = 6;
else if (queueSize >= 20) minScore = 5;
return [{json: {minScore}}];
```
5. **OpenAI Node** (GPT-5 Mini):
   - **System Prompt**: "Score this Slovak celebrity news 1-10 for viral potential. Consider: shock value, celebrity relevance, shareability. Return JSON: {score: 7, reasoning: '...', formats: ['headline', 'carousel']}"
   - **Enable Prompt Caching**: Yes
   - **Temperature**: 0.3 (judging task)
   - **Response Format**: JSON Object
6. **IF Node** - Check if `score >= minScore`
7. **Supabase Update** - Store `judge_score` and `format_assignments` (JSONB), mark `scored = TRUE`
8. **Supabase Update (False Branch)** - Mark `scored = TRUE`, `judge_score = 0` (rejected)

**Format Assignment Logic**:
- **Score 8-10**: `["podcast", "video", "carousel", "headline"]`
- **Score 6-7**: `["carousel", "headline"]`
- **Score 4-5**: `["headline"]`
- **Score 1-3**: `[]` (skip)

**API Keys Required**: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`

**Testing Strategy**:
- Test with different queue sizes: 10, 25, 45, 65
- Verify threshold changes correctly
- Check format assignments match score ranges
- Test rejection flow (score < minScore)

**Success Criteria**:
- [ ] Dynamic threshold adjusts based on queue size
- [ ] Scores articles accurately (spot-check 10-20 articles)
- [ ] Format assignments follow spec rules
- [ ] Rejected articles marked correctly (don't reprocess)

---

## Phase 2: Content Generation (Week 2-3)

### Status: Not Started

### Sub-Workflow 4: "Content Generator - Multi-Model Generation"

**Purpose**: 3 AI models (GPT-5 Mini, Claude Haiku 4.5, Gemini 2.5 Flash) each generate ALL assigned formats in ONE call

**Nodes**:
1. **Schedule Trigger** - Every 20 minutes
2. **Supabase Query** - Get scored articles with `format_assignments != '[]'` and no generated posts yet
3. **SplitInBatches** - Batch size: 5-10
4. **Split Into Branches** (3 parallel branches):
   - **Branch A: OpenAI Node** (GPT-5 Mini)
   - **Branch B: Anthropic Node** (Claude Haiku 4.5)
   - **Branch C: Google Gemini Node** (Gemini 2.5 Flash)
5. **Each Model Generates ALL Formats** in one call:
   - **System Prompt**: "Generate Slovak social media content for this celebrity news. Generate ALL requested formats in one response: headline, carousel (if requested), video script (if requested), podcast dialogue (if requested)."
   - **Enable Prompt Caching**: Yes
   - **Temperature**: 0.7 (creative task)
   - **Response Format**: JSON Object
6. **Supabase Insert** - Store each model's output in `posts` table (3 rows per article)

**Format Specifications**:

**Headline**: Max 140 characters, include emoji if relevant, scroll-stopping impact

**Carousel**: 3-8 slides, max 140 chars each, storytelling flow:
```json
{
  "slide_1": "Hook - shocking statement + emoji",
  "slide_2": "Detail 1",
  "slide_3": "Detail 2",
  ...
  "slide_n": "CTA or cliffhanger"
}
```

**Video Script**: 10-120 seconds, conversational tone:
```json
{
  "script": "Natural Slovak narration...",
  "duration_seconds": 45,
  "background_music_mood": "dramatic"
}
```

**Podcast Dialogue**: 2-person conversation (Male/Female hosts), 45-90 seconds:
```json
{
  "host_male": "Ahoj! Dnes máme šokujúcu správu...",
  "host_female": "Čo sa stalo?",
  "host_male": "...",
  ...
}
```

**API Keys Required**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_AI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`

**Testing Strategy**:
- Test each model separately first
- Verify all formats generated in ONE call (not 4 separate calls)
- Check Slovak language quality (natural, with slang)
- Measure token usage per model
- Compare model outputs for quality

**Success Criteria**:
- [ ] All 3 models generate content in parallel
- [ ] Each model generates ALL formats in ONE API call (4x token savings)
- [ ] Prompt caching enabled (90% savings on repeated prompts)
- [ ] Content stored correctly in `posts` table
- [ ] Cost: ~$0.01-0.03 per article (all 3 models combined)

---

### Sub-Workflow 5: "Second Judge - Best Version Selection"

**Purpose**: GPT-5 compares 3 versions per format and selects the best one

**Nodes**:
1. **Schedule Trigger** - Every 30 minutes
2. **Supabase Query** - Get articles with 3 generated posts (all models completed) but no selected post yet
3. **SplitInBatches** - Batch size: 10
4. **For Each Format** (headline, carousel, video, podcast):
   - **Code Node** - Group 3 versions by format
   - **OpenAI Node** (GPT-5) - Compare and judge:
     - **System Prompt**: "Compare these 3 Slovak social media posts. Choose the best one based on: virality, natural Slovak language, storytelling, engagement potential. Return: {winner: 'gpt-5-mini' | 'claude-haiku-4.5' | 'gemini-2.5-flash', score: 8, reasoning: '...'}"
     - **Temperature**: 0.3
     - **Response Format**: JSON Object
   - **Supabase Update** - Mark winner as `selected = TRUE`, store `judge_score`
   - **Supabase Update** - Update `model_performance` table (increment `judge_wins` for winner)

**API Keys Required**: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`

**Testing Strategy**:
- Test with 5-10 articles with all 3 versions
- Verify selection logic (winner marked correctly)
- Check model_performance table updates
- Spot-check judge decisions (are they reasonable?)

**Success Criteria**:
- [ ] Selects best version per format
- [ ] Updates model_performance tracking
- [ ] Stores judge reasoning for debugging
- [ ] Cost: ~$0.005 per article

---

## Phase 3: Media Creation (Week 4-5)

### Status: Not Started

### Sub-Workflow 6A: "Media Creator - Images"

**Purpose**: Extract images from source or generate with DALL-E, add text overlay

**Nodes**:
1. **Schedule Trigger** - Every 30 minutes
2. **Supabase Query** - Get selected posts needing images
3. **Code Node** - Try extract image from article HTML:
```javascript
const html = $json.raw_html;
const imgRegex = /<img[^>]+src="([^">]+)"/g;
const matches = [...html.matchAll(imgRegex)];
if (matches.length > 0) {
  return [{json: {image_url: matches[0][1], source: 'extracted'}}];
} else {
  return [{json: {source: 'generate'}}];
}
```
4. **IF Node** - Check if image extracted
5. **DALL-E Node** (False Branch) - Generate image:
   - **Prompt**: "Modern, bold, news-worthy image for: {article summary}"
   - **Size**: 1024x1024 (square for Instagram/Facebook)
6. **Code Node** - Add text overlay using Node.js canvas:
```javascript
const { createCanvas, loadImage } = require('canvas');
const canvas = createCanvas(1024, 1024);
const ctx = canvas.getContext('2d');

// Load image
const img = await loadImage($json.image_url);
ctx.drawImage(img, 0, 0, 1024, 1024);

// Semi-transparent overlay
ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
ctx.fillRect(0, 824, 1024, 200);

// Text
ctx.fillStyle = '#FFFFFF';
ctx.font = 'bold 48px Arial';
ctx.textAlign = 'center';
ctx.fillText($json.headline, 512, 924);

return [{json: {image_base64: canvas.toDataURL()}}];
```
7. **HTTP Request** - Upload to storage (Supabase Storage or Cloudinary)
8. **Supabase Update** - Store `media_urls` array in `posts` table

**API Keys Required**: `OPENAI_API_KEY` (DALL-E), `SUPABASE_URL`, `SUPABASE_KEY`

**Testing Strategy**:
- Test extraction with 10 sample articles
- Test DALL-E generation fallback
- Verify canvas overlay renders correctly
- Check uploaded images are accessible

**Success Criteria**:
- [ ] Extracts images when available (saves DALL-E costs)
- [ ] Generates images when needed
- [ ] Text overlay readable and attractive
- [ ] Images stored and URLs saved

---

### Sub-Workflow 6B: "Media Creator - Videos"

**Purpose**: Create TikTok/Reels format videos with voiceover, music, and captions

**Nodes**:
1. **Schedule Trigger** - Every 30 minutes
2. **Supabase Query** - Get selected posts with `content_type = 'video'` needing media
3. **ElevenLabs Node** - Generate voiceover:
   - **Voice**: Multilingual v2 model (Slovak support)
   - **Text**: Video script from `content.script`
4. **Whisper Node** - Generate captions:
   - **Audio**: Voiceover from step 3
   - **Language**: Slovak
   - **Format**: SRT
5. **Code Node** - Select background music:
```javascript
const mood = $json.content.background_music_mood;
const musicMap = {
  'upbeat': 'music/upbeat.mp3',
  'dramatic': 'music/dramatic.mp3',
  'sad': 'music/sad.mp3',
  'chill': 'music/chill.mp3',
  'energetic': 'music/energetic.mp3'
};
return [{json: {music_file: musicMap[mood] || musicMap['chill']}}];
```
6. **Code Node** - Assemble video with FFmpeg:
```javascript
const { exec } = require('child_process');

// Command: slideshow of images + voiceover + music (30% volume) + captions
const cmd = `
ffmpeg -loop 1 -i image1.jpg -loop 1 -i image2.jpg \
  -i voiceover.mp3 -i music.mp3 \
  -vf "subtitles=captions.srt" \
  -filter_complex "[1:a]volume=0.3[music];[0:a][music]amix=inputs=2[a]" \
  -map 0:v -map [a] -t ${duration} output.mp4
`;

exec(cmd, (error, stdout, stderr) => {
  // Handle output
});
```
7. **HTTP Request** - Upload to storage
8. **Supabase Update** - Store video URL in `media_urls`

**API Keys Required**: `ELEVENLABS_API_KEY`, `OPENAI_API_KEY` (Whisper), `SUPABASE_URL`, `SUPABASE_KEY`

**Testing Strategy**:
- Test voiceover quality (natural Slovak)
- Test caption accuracy
- Test FFmpeg assembly (manual verification)
- Check video plays correctly on mobile

**Success Criteria**:
- [ ] Voiceover sounds natural (Slovak accent)
- [ ] Captions accurate and synced
- [ ] Background music at 30% volume
- [ ] Video format works on TikTok/Instagram

---

### Sub-Workflow 6C: "Media Creator - Podcasts"

**Purpose**: Batch 5 high-scoring articles into podcast episodes with dialogue

**Nodes**:
1. **Schedule Trigger** - Every 6 hours
2. **Supabase Query** - Get 5 selected posts with `content_type = 'podcast'` and `judge_score >= 8`
3. **OpenAI Node** - Generate episode structure:
   - **System Prompt**: "Create a 5-segment podcast episode from these Slovak celebrity news items. Include: intro, transitions between stories, outro. Each segment 45-90 seconds."
   - **Temperature**: 0.7
4. **For Each Segment**:
   - **ElevenLabs Node (Male Voice)** - Generate male host audio
   - **ElevenLabs Node (Female Voice)** - Generate female host audio
5. **Code Node** - Concatenate audio segments with FFmpeg:
```javascript
const { exec } = require('child_process');

// Concatenate: intro + segment1 + transition1 + segment2 + ... + outro
const cmd = `
ffmpeg -i intro.mp3 -i segment1.mp3 -i transition1.mp3 ... -i outro.mp3 \
  -filter_complex "[0:0][1:0][2:0]...[n:0]concat=n=${count}:v=0:a=1[out]" \
  -map "[out]" podcast_episode.mp3
`;

exec(cmd, ...);
```
6. **Code Node** - Create YouTube video (audio + visualizer):
```javascript
// FFmpeg: audio waveform visualizer + slideshow
const cmd = `
ffmpeg -i podcast.mp3 -i logo.png \
  -filter_complex "[0:a]showwaves=s=1920x1080:mode=line[waves];[waves][1:v]overlay=10:10[v]" \
  -map "[v]" -map 0:a -t ${duration} youtube_video.mp4
`;
```
7. **HTTP Request** - Upload to storage
8. **Supabase Update** - Store podcast/video URLs

**API Keys Required**: `ELEVENLABS_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`

**Testing Strategy**:
- Test 5-article batch processing
- Verify dialogue sounds natural (male/female alternation)
- Check transitions are smooth
- Test YouTube video rendering

**Success Criteria**:
- [ ] Batches 5 articles per episode
- [ ] Dialogue flows naturally
- [ ] Total duration 5-10 minutes
- [ ] YouTube video looks professional

---

## Phase 4: Publishing (Week 6-7)

### Status: Not Started

### Sub-Workflow 7: "Publisher - Multi-Platform Posting"

**Purpose**: Post to Instagram, Facebook, TikTok, YouTube with rate limiting

**Nodes**:
1. **Schedule Trigger** - 6 times per day (7am, 10am, 1pm, 4pm, 7pm, 10pm)
2. **Supabase Query** - Get queue of selected posts (`selected = TRUE`, `posted = FALSE`)
3. **Code Node** - Check rate limits:
```javascript
const now = new Date();
const recentPosts = $json.recent_posts; // Last 24 hours

// Instagram/Facebook: Max 1 per window (3 hours apart)
const instagramCount = recentPosts.filter(p => p.platform === 'instagram' &&
  (now - new Date(p.posted_at)) < 3*60*60*1000).length;

if (instagramCount > 0) {
  return [{json: {can_post_instagram: false}}];
} else {
  return [{json: {can_post_instagram: true}}];
}

// Similar logic for other platforms
```
4. **IF Node** - Check if can post
5. **Switch Node** - Route by platform:
   - **Instagram**: HTTP Request to Graph API
   - **Facebook**: HTTP Request to Graph API
   - **YouTube**: HTTP Request to YouTube Data API
   - **TikTok**: Manual upload (alert user)
6. **Supabase Update** - Mark `posted = TRUE`, store `posted_at` and `post_url`
7. **Discord Webhook** (Optional) - Notify team of new post

**Rate Limits**:
- **Instagram/Facebook**: 1 post per window (6/day max, 3 hours apart)
- **YouTube**: 2-3 videos/day
- **TikTok**: Manual upload (8-10/day target)

**API Keys Required**: `FB_PAGE_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID`, `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `DISCORD_WEBHOOK_URL` (optional), `SUPABASE_URL`, `SUPABASE_KEY`

**Testing Strategy**:
- Test with test accounts first (Instagram test account, etc.)
- Verify rate limiting logic (don't post twice in 3 hours)
- Test each platform API separately
- Monitor for API errors (rate limits, auth failures)

**Success Criteria**:
- [ ] Posts to Instagram/Facebook 6 times per day max
- [ ] Posts to YouTube 2-3 times per day
- [ ] Respects 3-hour spacing between posts
- [ ] Handles API errors gracefully (retry with backoff)

---

## Phase 5: Performance Tracking (Week 8-9)

### Status: Not Started

### Sub-Workflow 8: "Performance Tracker - Engagement Metrics"

**Purpose**: Measure engagement at 1hr, 6hr, 24hr checkpoints; feed data back to judges

**Nodes**:
1. **Schedule Trigger** - Every hour
2. **Supabase Query** - Get posts needing metrics collection:
   - 1hr checkpoint: `posted_at` between 60-70 minutes ago
   - 6hr checkpoint: `posted_at` between 6-7 hours ago
   - 24hr checkpoint: `posted_at` between 24-25 hours ago
3. **Switch Node** - Route by platform
4. **Platform-Specific Metrics Collection**:
   - **Instagram**: HTTP Request to Graph API (likes, comments, saves, views)
   - **Facebook**: HTTP Request to Graph API (likes, comments, shares)
   - **YouTube**: HTTP Request to YouTube Data API (views, likes, comments)
   - **TikTok**: Manual entry (for MVP)
5. **Code Node** - Calculate engagement rate:
```javascript
const { likes, comments, shares, views } = $json;
const engagements = likes + (comments * 2) + (shares * 3);
const engagement_rate = (engagements / views) * 100;

return [{json: { engagement_rate: engagement_rate.toFixed(2) }}];
```
6. **Supabase Insert** - Store in `performance_metrics` table
7. **Supabase Update** - Update `model_performance` (rolling average)

**Feedback Loop to Judges**:
- High-performing content characteristics inform future scoring
- Underperforming models get lower weights in second judge
- Track which formats perform best per platform

**API Keys Required**: `FB_PAGE_ACCESS_TOKEN`, `INSTAGRAM_ACCOUNT_ID`, `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `SUPABASE_URL`, `SUPABASE_KEY`

**Testing Strategy**:
- Test checkpoint timing (posts collected at right times)
- Verify engagement rate calculation
- Check model_performance updates correctly
- Test feedback loop (spot-check judge decisions change)

**Success Criteria**:
- [ ] Collects metrics at 1hr, 6hr, 24hr checkpoints
- [ ] Engagement rate calculated correctly
- [ ] Model performance tracked over time
- [ ] Data feeds back to improve future judging

---

## Phase 6: Testing & Launch (Week 10-12)

### Status: Not Started

### Integration Testing
- [ ] Test complete pipeline end-to-end with small batch (5-10 articles)
- [ ] Monitor execution logs for errors
- [ ] Verify data flows correctly between sub-workflows
- [ ] Check error handling (disconnect, API failures)

### Cost Validation
- [ ] Track token usage per sub-workflow
- [ ] Calculate daily cost (target: ~$4.30/day)
- [ ] Verify prompt caching is working (90% savings)
- [ ] Check batch processing reduces calls

### Performance Testing
- [ ] Measure execution time per sub-workflow
- [ ] Test queue processing speed (can handle 30 posts/day?)
- [ ] Check rate limiting works correctly
- [ ] Monitor Supabase performance (query speed)

### Soft Launch
- [ ] Start with 1-2 articles per day
- [ ] Post to test accounts only
- [ ] Monitor engagement metrics
- [ ] Collect user feedback
- [ ] Gradually increase to 30 posts/day

### Production Monitoring
- [ ] Set up Discord alerts for critical errors
- [ ] Monitor daily costs (stay within budget)
- [ ] Track model performance over time
- [ ] Review engagement metrics weekly
- [ ] Adjust judge thresholds based on data

---

## Development Workflow (Per Sub-Workflow)

### Step-by-Step Process:
1. **Discover** - Search for relevant nodes (`search_nodes`, `search_templates`)
2. **Configure** - Get node essentials with examples (`get_node_essentials`)
3. **Validate** - Validate each node (`validate_node_minimal` → `validate_node_operation`)
4. **Build** - Construct workflow JSON with validated configs
5. **Test** - Validate complete workflow (`validate_workflow`)
6. **Deploy** - Create workflow in n8n (`n8n_create_workflow`)
7. **Verify** - Post-deployment validation (`n8n_validate_workflow`)

### Testing Checklist (Per Sub-Workflow):
- [ ] **Functional**: Does it execute without errors?
- [ ] **Data Quality**: Is output format correct?
- [ ] **Performance**: Execution time acceptable?
- [ ] **Error Handling**: Graceful failures?
- [ ] **Cost**: Token usage within budget?

---

## Key Tools & Skills

### Primary n8n-MCP Tools:
- `search_nodes` / `get_node_essentials` - Node discovery and configuration
- `validate_node_operation` / `validate_workflow` - Validation
- `n8n_create_workflow` / `n8n_update_partial_workflow` - Deployment

### Primary n8n-Skills:
- **n8n-mcp-tools-expert** - Tool usage guidance
- **n8n-workflow-patterns** - Architecture patterns
- **n8n-validation-expert** - Error fixing
- **n8n-code-javascript** - Media processing

---

## Critical Success Factors

### ✅ Do's:
- Enable prompt caching on all LLM nodes (90% savings)
- Generate all 4 formats in ONE call per model (4x token reduction)
- Use batch processing (10-20 articles per call)
- Validate iteratively (expect 2-3 cycles per node)
- Test with sample data before real scraping
- Monitor costs daily

### ❌ Don'ts:
- Don't build monolithic workflow (use sub-workflows)
- Don't skip validation steps
- Don't forget queue-based strictness logic
- Don't hardcode credentials (use n8n credentials system)
- Don't manually activate workflows (n8n-mcp cannot activate, use UI)

---

## Cost Optimization Checklist

From spec (~$4.30/day target):
- [ ] GPT-5 Nano for extraction (cheapest model)
- [ ] Prompt caching enabled on all LLM nodes
- [ ] Generate all 4 formats in ONE call per model (not 4 separate calls)
- [ ] Batch processing (10-20 articles per API call)
- [ ] Queue-based strictness (reject low scores when queue full)
- [ ] Model performance tracking (drop underperforming models)
- [ ] Conditional generation (score < threshold = skip)

---

## Estimated Timeline

- **Phase 0 (Setup)**: 1-2 hours
- **Phase 1 (Data Collection)**: 1-2 days
- **Phase 2 (Content Generation)**: 3-4 days
- **Phase 3 (Media Creation)**: 5-7 days
- **Phase 4 (Publishing)**: 3-4 days
- **Phase 5 (Tracking)**: 2-3 days
- **Phase 6 (Testing & Launch)**: 5-7 days

**Total**: 10-12 weeks to MVP

---

## Status Legend

- **Not Started**: Component not yet begun
- **In Progress**: Currently being developed
- **Testing**: Built, undergoing validation
- **Completed**: Deployed and verified
- **Blocked**: Waiting on dependencies (API keys, etc.)

---

## Next Steps

1. Complete Phase 0 setup (Supabase + API keys)
2. Build Sub-Workflow 1A (Scraper) - Simplest component, no LLM
3. Build Sub-Workflow 1B (Extraction) - Test GPT-5 Nano + prompt caching
4. Build Sub-Workflow 1C (First Judge) - Test queue-based logic
5. Iterate through remaining phases

---

*Last Updated: 2025-11-03*
