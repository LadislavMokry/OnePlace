# Content Automation System (Manual Intake First)
## Technical Specification Document (MVP)

**Version:** 1.0  
**Last Updated:** January 5, 2026
**Target Platform:** Python (FastAPI + worker scripts)
**Content Language:** Configurable (default Slovak)
**Scope Update (2026-01-05):** Video-first outputs (shorts + audio roundup). Multi-format outputs deferred; generation uses full content; second judge selects best variant.

---

## Table of Contents

1. [Overview & Architecture](#overview--architecture)
2. [System Components](#system-components)
3. [Component Details](#component-details)
4. [Configuration & Settings](#configuration--settings)
5. [Testing](#testing)
6. [Error Handling & Monitoring](#error-handling--monitoring)
7. [Cost Estimates](#cost-estimates)
8. [Implementation Notes](#implementation-notes)

---

## Overview & Architecture
Update Notice (2025-12-30): Implementation is Python-first. n8n workflow references are legacy.

### Project Goal
Automated content generation and publishing system for uploaded text (PDF/DOCX/TXT or pasted text) plus web scraping, across multiple social media platforms (Instagram, Facebook, TikTok, YouTube). The MVP is topic-agnostic.

### High-Level Workflow
```
Manual Intake (upload/paste) → Storage (Supabase) →
Scraping (sources) → Storage (Supabase) →
Extraction (condense) → First Judge → Content Generation →
Second Judge → Media Creation → Publishing → Performance Tracking
```
Scraping and manual intake both feed the same downstream pipeline.

### Key Principles
- **Modular design**: Easy to swap sources, models, and platforms
- **Quality-driven**: Dynamic judge strictness based on queue size
- **Cost-optimized**: Prompt caching, conditional generation, parallel processing
- **Data-driven**: Track model performance and engagement metrics

---

## System Components

### 1. Ingestion Module (Manual Intake)
**Purpose:** Ingest uploaded text (PDF/DOCX/TXT or pasted text) into the database
**Input:** Uploaded files or pasted text
**Output:** Plain text chunks stored as article rows

### 1B. Data Collection Module (Scraping)
**Purpose:** Scrape project sources (RSS/Reddit/page/YouTube) into `source_items` for ingestion.
**Input:** Source URLs
**Output:** Raw HTML stored in `articles` (or a dedicated table if added later)

### 2. Storage & Deduplication Module
**Purpose:** Store articles in database, prevent duplicate processing  
**Input:** Article data  
**Output:** Cleaned article records with unique IDs  

### 3. Extraction Module
**Purpose:** Condense HTML to clean summaries (reduce token costs)  
**Input:** Raw HTML (50k-100k tokens)  
**Output:** Article summary (~500 tokens)  

### 4. First Judge Module
**Purpose:** Score articles, assign content format treatment  
**Input:** Article summaries  
**Output:** Scores (1-10), format assignments  

### 5. Content Generation Module
**Purpose:** Create multiple versions of content in all required formats  
**Input:** High-scoring articles  
**Output:** Headlines, carousels, video scripts, podcast segments  

### 6. Second Judge Module
**Purpose:** Select best version from multiple model outputs  
**Input:** Multiple versions per format  
**Output:** Winning content for each format  

### 7. Media Creation Module
**Purpose:** Generate images, videos, and audio files  
**Input:** Content from generators  
**Output:** Ready-to-post media files  

### 8. Publishing Module
**Purpose:** Post content to social platforms with rate limiting  
**Input:** Finalized content + media  
**Output:** Posted content across platforms  

### 9. Performance Tracking Module
**Purpose:** Measure engagement, feed data back to judges
**Input:** Posted content IDs
**Output:** Metrics stored in database

---

## Testing

### Intake API
- `/health` returns `{"status":"ok"}`
- `/intake/text` inserts 1+ rows into `articles`
- `/intake/file` extracts PDF/DOCX/TXT and inserts 1+ rows

### Scraping
- `python -m app.worker scrape` inserts raw HTML rows
- One failing source does not stop the job

### Database
- `source_url` unique constraint prevents duplicates
- `processed` and `scored` defaults are `false`

---

## Component Details

## 1. Ingestion Module (Manual Intake)

### Inputs Supported
- Uploaded files: PDF, DOCX, TXT
- Pasted text via JSON

### Behavior
- Extract text and split by headings (Chapter/Kapitola/Part/Book)
- If no headings, chunk to ~2500 words
- Insert each chunk into `articles` with `source_website = "manual"`

### Notes
- `raw_html` stores extracted plain text (schema compatibility)
- Text-based PDFs work best; scanned PDFs require OCR (not included)

---
## 1B. Data Collection Module (Deferred: Web Scraping)

### Source Websites (Deferred - Celebrity/Gossip Focus)
- https://www.topky.sk/
- https://www.cas.sk/
- https://www1.pluska.sk/
- https://refresher.sk/
- https://www.startitup.sk/

### n8n Nodes Required
- **Schedule Trigger** node (cron: every hour)
- **HTTP Request** nodes (one per website)
- **Function** node (optional, for RSS feed detection)

### Implementation Steps

#### Step 1: Set up Schedule Trigger
- Add **Schedule Trigger** node
- Set to run: `0 * * * *` (every hour on the hour)
- This initiates the entire workflow

#### Step 2: Check for RSS Feeds (Optimization)
For each website, first attempt RSS:
- Add **HTTP Request** node
- Method: GET
- URL: `{website}/rss` or `{website}/feed`
- Error handling: Continue on fail
- If successful, parse RSS XML; if fails, proceed to HTML scraping

#### Step 3: HTML Scraping (Fallback)
If no RSS feed available:
- Add **HTTP Request** node per website
- Method: GET
- URL: Target website homepage/news section
- Headers: 
  ```
  User-Agent: Mozilla/5.0 (compatible; NewsBot/1.0)
  Accept: text/html
  ```
- Ignore SSL issues: OFF
- Timeout: 30 seconds

#### Step 4: Handle Failures
- Add **IF** node after each scraper
- Condition: Check if response status = 200
- If website down: Continue workflow with remaining sources
- Log failure for monitoring

### Testing Checklist
- [ ] Schedule triggers hourly
- [ ] Each website scraped successfully
- [ ] RSS parsing works (if available)
- [ ] Failed scrapes don't crash workflow
- [ ] HTML responses stored correctly

---

## 2. Storage & Deduplication Module

### Database: Supabase (PostgreSQL)

### Required Tables

#### `articles` table
```sql
CREATE TABLE articles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_url TEXT NOT NULL,
  source_website TEXT NOT NULL,
  title TEXT,
  content TEXT,
  summary TEXT, -- Condensed by extraction module
  scraped_at TIMESTAMP DEFAULT NOW(),
  processed BOOLEAN DEFAULT FALSE,
  judge_score INTEGER, -- 1-10 rating from first judge
  format_assignments JSONB, -- {podcast: true, video: true, carousel: true, headline: true}
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(source_url) -- Prevent duplicates
);

CREATE INDEX idx_articles_processed ON articles(processed);
CREATE INDEX idx_articles_score ON articles(judge_score);
CREATE INDEX idx_articles_scraped ON articles(scraped_at);
```

#### `posts` table
```sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  article_id UUID REFERENCES articles(id),
  platform TEXT NOT NULL, -- 'instagram', 'facebook', 'tiktok', 'youtube'
  content_type TEXT NOT NULL, -- 'headline', 'carousel', 'video', 'podcast'
  generating_model TEXT NOT NULL, -- 'gpt-5-mini', 'haiku-4.5', 'gemini-2.5-flash'
  judge_score INTEGER, -- Second judge rating
  content JSONB, -- Actual post content (text, captions, etc.)
  media_urls TEXT[], -- Links to generated images/videos
  posted_at TIMESTAMP,
  post_url TEXT, -- URL of published post
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_posts_article ON posts(article_id);
CREATE INDEX idx_posts_platform ON posts(platform);
CREATE INDEX idx_posts_model ON posts(generating_model);
```

#### `performance_metrics` table
```sql
CREATE TABLE performance_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id UUID REFERENCES posts(id),
  checked_at TIMESTAMP NOT NULL,
  checkpoint TEXT NOT NULL, -- '1hr', '6hr', '24hr'
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  views INTEGER DEFAULT 0,
  engagement_rate FLOAT, -- Calculated metric
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_metrics_post ON performance_metrics(post_id);
CREATE INDEX idx_metrics_checkpoint ON performance_metrics(checkpoint);
```

#### `model_performance` table (for feedback loop)
```sql
CREATE TABLE model_performance (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  model_name TEXT NOT NULL,
  content_type TEXT NOT NULL,
  judge_wins INTEGER DEFAULT 0, -- Times this model won second judge
  avg_engagement FLOAT, -- Average engagement across all posts
  total_posts INTEGER DEFAULT 0,
  last_updated TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_model_content ON model_performance(model_name, content_type);
```

### n8n Nodes Required
- **Supabase** node (for inserts/queries)
- **Postgres** node (for complex queries)
- **Function** node (for data transformation)

### Implementation Steps

#### Step 1: Connect to Supabase
- Create Supabase project (free tier sufficient for MVP)
- Get connection details from Settings → Database → Connection String
- In n8n, add **Supabase** credential:
  - Host: From connection string
  - Database: postgres
  - User: postgres
  - Password: Your database password
  - Port: 5432
  - SSL: Enable

#### Step 2: Insert Scraped Articles
After Data Collection module:
- Add **Function** node to transform scraped data:
```javascript
// Extract relevant fields from HTML/RSS
const items = $input.all();
const articles = items.map(item => ({
  source_url: item.json.url,
  source_website: item.json.website,
  title: item.json.title || 'No title',
  content: item.json.fullText || item.json.html,
  scraped_at: new Date().toISOString()
}));

return articles;
```

- Add **Supabase** node:
  - Operation: Insert
  - Table: articles
  - Data: From Function node output
  - Options: 
    - On Conflict: Do Nothing (prevents duplicate URL insertion)
    - Return Fields: id, source_url

#### Step 3: Query Unprocessed Articles
To build queue for judging:
- Add **Supabase** node:
  - Operation: Get Many
  - Table: articles
  - Filters:
    - processed = false
    - scraped_at > (NOW() - INTERVAL '48 hours') -- Delete old articles
  - Sort: scraped_at DESC
  - Limit: 100 (or adjust based on expected volume)

#### Step 4: Check Queue Size (for dynamic judging)
- Add **Postgres** node:
```sql
SELECT COUNT(*) as queue_size 
FROM articles 
WHERE processed = false 
AND scraped_at > NOW() - INTERVAL '48 hours';
```
- Store result in workflow variable for First Judge module

#### Step 5: Delete Stale Articles
Run periodically (e.g., daily):
- Add **Postgres** node:
```sql
DELETE FROM articles 
WHERE processed = false 
AND scraped_at < NOW() - INTERVAL '48 hours';
```

### Testing Checklist
- [ ] Supabase connection works
- [ ] Articles insert without duplicates
- [ ] Queue query returns unprocessed articles
- [ ] Stale articles deleted after 48 hours
- [ ] Queue size calculation accurate

---

## 3. Extraction Module

### Purpose
Reduce token costs by condensing raw HTML (50k-100k tokens) to clean article summaries (~500 tokens) before sending to expensive judge models.

### Model: GPT-5 Nano (cheapest)
- **Pricing:** $0.15 input / $1.50 output per million tokens
- **Why Nano:** Simple extraction task, doesn't need reasoning power

### n8n Nodes Required
- **OpenAI** node (Chat Model)
- **Function** node (data formatting)

### Implementation Steps

#### Step 1: Prepare Article Data
- Add **Function** node after Storage module:
```javascript
// Format articles for LLM processing
const items = $input.all();
return items.map(item => ({
  json: {
    article_id: item.json.id,
    raw_content: item.json.content,
    source_url: item.json.source_url
  }
}));
```

#### Step 2: Extract with GPT-5 Nano
- Add **OpenAI** node:
  - Operation: Message a Model
  - Model: gpt-5-nano
  - System Message:
```
You are an article extraction specialist. Extract ONLY the following from the HTML:
- Article title
- Main content (article body text only - no navigation, ads, or comments)
- Publication date (if available)
- Key people/celebrities mentioned
- Main topic/category (e.g., "celebrity breakup", "scandal", "fashion")

Return in this exact JSON format:
{
  "title": "...",
  "content": "...",
  "date": "...",
  "people": ["person1", "person2"],
  "topic": "..."
}

Be concise. Remove all HTML tags, scripts, and formatting. Maximum 500 words for content.
```
  - User Message: `{{ $json.raw_content }}`
  - Temperature: 0.1 (low creativity, factual extraction)
  - Max Tokens: 1000

#### Step 3: Parse and Store Summary
- Add **Function** node:
```javascript
// Parse LLM output and prepare for database update
const items = $input.all();
return items.map(item => {
  const extracted = JSON.parse(item.json.choices[0].message.content);
  return {
    json: {
      id: item.json.article_id,
      summary: JSON.stringify(extracted), // Store as JSONB
      title: extracted.title
    }
  };
});
```

- Add **Supabase** node:
  - Operation: Update
  - Table: articles
  - Update Key: id
  - Data: 
    - summary = {{ $json.summary }}
    - title = {{ $json.title }}

### Optimization: Parallel Processing
- Add **SplitInBatches** node before OpenAI:
  - Batch Size: 10
  - This processes 10 articles simultaneously
  - Reduces total processing time

### Testing Checklist
- [ ] Raw HTML successfully condensed
- [ ] Extraction removes ads/navigation
- [ ] JSON parsing works correctly
- [ ] Summaries stored in database
- [ ] Parallel processing reduces time
- [ ] Token usage stays under 2k per article

---

## 4. First Judge Module

### Purpose
Score articles (1-10) and assign content format treatment based on quality.

### Model: GPT-5 (full reasoning model)
- **Pricing:** $1.25 input / $10 output per million tokens
- **Why GPT-5:** Needs strong reasoning for quality assessment

### Scoring Criteria
- Virality potential (celebrity prominence, controversy, emotional impact)
- Timeliness (breaking news scores higher)
- Visual potential (can it make compelling images/videos?)
- Audience relevance (Slovak celebrity/gossip focus)

### Format Assignment Logic
- **Score 8-10:** Podcast + Video + Carousel + Headline
- **Score 6-7:** Carousel + Headline
- **Score 4-5:** Headline only
- **Score 1-3:** Skip (don't generate content)

### Dynamic Strictness (Queue-based)
```javascript
// Adjust passing threshold based on queue size
const queueSize = $node["CheckQueueSize"].json.queue_size;

let passingThreshold;
if (queueSize < 20) {
  passingThreshold = 4; // Accept scores 4+
} else if (queueSize < 40) {
  passingThreshold = 5; // Accept scores 5+
} else if (queueSize < 60) {
  passingThreshold = 6; // Accept scores 6+
} else {
  passingThreshold = 7; // Only top content (7+)
}
```

### n8n Nodes Required
- **OpenAI** node (GPT-5)
- **Function** nodes (data prep, scoring logic)
- **IF** node (conditional routing)

### Implementation Steps

#### Step 1: Fetch Performance Data (for feedback loop)
Before judging, get trending topics:
- Add **Postgres** node:
```sql
SELECT 
  p.content->>'topic' as topic,
  AVG(pm.engagement_rate) as avg_engagement,
  COUNT(*) as post_count
FROM posts p
JOIN performance_metrics pm ON p.id = pm.post_id
WHERE p.posted_at > NOW() - INTERVAL '7 days'
AND pm.checkpoint = '24hr'
GROUP BY topic
HAVING COUNT(*) >= 3
ORDER BY avg_engagement DESC
LIMIT 10;
```
- Store in workflow variable: `trendingTopics`

#### Step 2: Prepare Judge System Prompt
- Add **Function** node:
```javascript
const queueSize = $node["CheckQueueSize"].json.queue_size;
const trending = $node["FetchTrendingTopics"].json;

// Build trending topics string
const trendingStr = trending.map(t => 
  `${t.topic} (${t.avg_engagement.toFixed(2)}% engagement)`
).join(', ');

// Determine strictness message
let strictness = "";
if (queueSize > 60) {
  strictness = "CRITICAL: Queue is full. Be EXTREMELY selective. Only rate 8+ for truly exceptional content.";
} else if (queueSize > 40) {
  strictness = "WARNING: Queue is growing. Be strict. Only rate 6+ for good content.";
} else if (queueSize > 20) {
  strictness = "NOTICE: Moderate queue. Maintain standards. Rate 5+ for acceptable content.";
} else {
  strictness = "Normal queue size. Use standard criteria. Rate 4+ for passable content.";
}

return [{
  json: {
    systemPrompt: `You are a celebrity gossip content judge for a Slovak social media audience.

SCORING CRITERIA (1-10):
- Virality potential: Will this capture attention? Controversy, drama, emotion?
- Celebrity prominence: Are these well-known Slovak/international celebrities?
- Timeliness: Is this breaking news or stale?
- Visual potential: Can this make compelling images/videos?
- Audience relevance: Does this fit Slovak celebrity/entertainment interests?

TRENDING TOPICS (prioritize these): ${trendingStr}

QUEUE STATUS: ${queueSize} articles waiting
${strictness}

RESPONSE FORMAT (JSON only, no other text):
{
  "score": <1-10>,
  "reasoning": "<why this score>",
  "topic": "<main category: celebrity_breakup, scandal, fashion, music, etc.>",
  "format_assignment": {
    "podcast": <true/false>,
    "video": <true/false>,
    "carousel": <true/false>,
    "headline": <true/false>
  }
}

FORMAT ASSIGNMENT RULES:
- Score 8-10: All formats (podcast, video, carousel, headline)
- Score 6-7: carousel + headline only
- Score 4-5: headline only
- Score 1-3: No formats (will be skipped)`
  }
}];
```

#### Step 3: Judge Each Article
- Add **SplitInBatches** node (batch size: 5 for parallel judging)
- Add **OpenAI** node:
  - Model: gpt-5
  - System Message: `{{ $node["PrepareJudgePrompt"].json.systemPrompt }}`
  - User Message:
```
ARTICLE TO JUDGE:
Title: {{ $json.title }}
Summary: {{ $json.summary }}
Source: {{ $json.source_website }}
Scraped: {{ $json.scraped_at }}

Provide your judgment in JSON format.
```
  - Temperature: 0.3 (some creativity but mostly consistent)
  - Max Tokens: 500
  - Response Format: JSON Object
  
#### Step 4: Parse Judge Output
- Add **Function** node:
```javascript
const items = $input.all();
return items.map(item => {
  const judgment = JSON.parse(item.json.choices[0].message.content);
  return {
    json: {
      article_id: item.json.article_id,
      judge_score: judgment.score,
      reasoning: judgment.reasoning,
      topic: judgment.topic,
      format_assignments: judgment.format_assignment
    }
  };
});
```

#### Step 5: Filter by Passing Threshold
- Add **Function** node:
```javascript
const queueSize = $node["CheckQueueSize"].json.queue_size;
const items = $input.all();

// Determine threshold
let threshold;
if (queueSize < 20) threshold = 4;
else if (queueSize < 40) threshold = 5;
else if (queueSize < 60) threshold = 6;
else threshold = 7;

// Filter articles that pass
return items.filter(item => item.json.judge_score >= threshold);
```

#### Step 6: Update Database
- Add **Supabase** node:
  - Operation: Update
  - Table: articles
  - Update Key: article_id
  - Data:
    - judge_score = {{ $json.judge_score }}
    - format_assignments = {{ $json.format_assignments }}
    - processed = true (mark as judged)

### Optimization: Prompt Caching
Enable caching for system prompt (saves 90% on repeated calls):
- In OpenAI node settings:
  - Enable prompt caching
  - Cache TTL: 3600 seconds
  - Since system prompt rarely changes, most requests will hit cache

### Testing Checklist
- [ ] Trending topics fetched correctly
- [ ] Queue size affects strictness
- [ ] Judge scores reasonably (validate sample)
- [ ] Format assignments follow rules
- [ ] Low-scoring articles filtered out
- [ ] Database updated with scores
- [ ] Prompt caching reduces costs

---

## 5. Content Generation Module

### Purpose
Generate multiple versions of content in all required formats using 3 different LLMs.

### Models
1. **GPT-5 Mini** - $0.50 input / $5 output per million tokens
2. **Claude Haiku 4.5** - $1 input / $5 output per million tokens
3. **Gemini 2.5 Flash** - Competitive pricing, varies by region

### Strategy
- Each model generates ALL assigned formats in ONE API call
- Reduces input token costs (article sent once per model, not 4x)
- Enables model performance comparison

### n8n Nodes Required
- **OpenAI** node (GPT-5 Mini)
- **Anthropic Chat Model** node (Haiku 4.5)
- **Google Gemini Chat Model** node (Gemini 2.5 Flash)
- **Function** nodes (prompting, parsing)
- **Merge** node (combine outputs)

### Implementation Steps

#### Step 1: Filter Articles by Format Needs
- Add **Switch** node based on score:
  - Case 1: score >= 8 → Generate all 4 formats
  - Case 2: score >= 6 → Generate carousel + headline
  - Case 3: score >= 4 → Generate headline only

#### Step 2: Prepare Generation Prompt
- Add **Function** node:
```javascript
const article = $input.item(0).json;
const formats = article.format_assignments;

// Build format instructions
let instructions = "";
if (formats.headline) {
  instructions += `
1. HEADLINE (burst post - quick impact):
   - 1 punchy line (max 140 characters)
   - Include emoji if relevant
   - Optimize for scroll-stopping impact
`;
}

if (formats.carousel) {
  instructions += `
2. CAROUSEL (3-8 slides):
   - Break story into digestible chunks
   - Each slide: max 140 characters
   - First slide: hook/headline
   - Middle slides: key details
   - Last slide: takeaway/call-to-action
   - Return as array: ["slide 1", "slide 2", ...]
`;
}

if (formats.video) {
  instructions += `
3. VIDEO SCRIPT (short-form, 10-120 seconds):
   - Write conversational narration
   - Match length to story complexity
   - Include pauses for dramatic effect
   - Suggest background_music_mood: "upbeat", "dramatic", "chill", "sad", or "energetic"
   - Estimate duration in seconds
`;
}

if (formats.podcast) {
  instructions += `
4. PODCAST SEGMENT (for 5-article compilation):
   - Write as 2-person dialogue (Male host, Female host)
   - Conversational, engaging tone
   - Cover story thoroughly but concisely (45-90 seconds)
   - Use Slovak slang and cultural references
   - Format: 
     Male: "opening line"
     Female: "response"
     Male: "follow-up"
     etc.
`;
}

return [{
  json: {
    article: article,
    prompt: `You are a Slovak celebrity gossip content creator. Generate social media content for this story.

ARTICLE:
${JSON.stringify(article.summary)}

GENERATE THE FOLLOWING FORMATS:
${instructions}

STYLE GUIDELINES:
- Write in fluent, natural Slovak language
- Be engaging, dramatic where appropriate
- Use cultural references Slovak audience understands
- Optimize for virality and engagement

RETURN JSON ONLY (no other text):
${JSON.stringify({
  headline: formats.headline ? "..." : null,
  carousel: formats.carousel ? ["slide1", "slide2"] : null,
  video: formats.video ? {
    script: "...",
    duration_seconds: 30,
    background_music_mood: "upbeat"
  } : null,
  podcast: formats.podcast ? {
    dialogue: [
      {speaker: "Male", text: "..."},
      {speaker: "Female", text: "..."}
    ]
  } : null
})}`
  }
}];
```

#### Step 3: Generate with GPT-5 Mini
- Add **OpenAI** node:
  - Model: gpt-5-mini
  - System Message: "You are a Slovak celebrity gossip content expert. Always respond with valid JSON."
  - User Message: `{{ $json.prompt }}`
  - Temperature: 0.7 (creative but controlled)
  - Max Tokens: 2000
  - Response Format: JSON Object

#### Step 4: Generate with Haiku 4.5
- Add **Anthropic Chat Model** node:
  - Model: claude-haiku-4-5
  - System Message: Same as above
  - User Message: `{{ $json.prompt }}`
  - Temperature: 0.7
  - Max Tokens: 2000

#### Step 5: Generate with Gemini 2.5 Flash
- Add **Google Gemini Chat Model** node:
  - Model: gemini-2.5-flash
  - System Message: Same as above
  - User Message: `{{ $json.prompt }}`
  - Temperature: 0.7
  - Max Tokens: 2000

#### Step 6: Tag Outputs by Model
- Add **Function** node after each model:
```javascript
// GPT-5 Mini output
return $input.all().map(item => ({
  json: {
    article_id: item.json.article_id,
    model: "gpt-5-mini",
    generated_content: JSON.parse(item.json.choices[0].message.content)
  }
}));

// Repeat similar for Haiku and Gemini with appropriate parsing
```

#### Step 7: Merge All Model Outputs
- Add **Merge** node:
  - Mode: Append
  - Combine outputs from all 3 models
  - Result: 3 versions of each format per article

### Optimization: Parallel Execution
- Use n8n's parallel branches:
  - Split after "Prepare Generation Prompt"
  - Run all 3 models simultaneously
  - Merge results
  - This reduces total time by ~66%

### Testing Checklist
- [ ] Correct formats generated based on score
- [ ] All 3 models produce valid JSON
- [ ] Slovak language quality is good
- [ ] Carousel slides follow character limits
- [ ] Video scripts suggest appropriate mood
- [ ] Podcast dialogues are conversational
- [ ] Parallel execution works correctly
- [ ] Outputs tagged with model name

---

## 6. Second Judge Module

### Purpose
Compare outputs from 3 models and select the best version for each format.

### Model: GPT-5 (full reasoning)
- **Pricing:** $1.25 input / $10 output per million tokens
- **Why:** Needs strong reasoning to compare quality

### n8n Nodes Required
- **OpenAI** node (GPT-5)
- **Function** nodes (grouping, parsing)
- **Aggregate** node (group by article)

### Implementation Steps

#### Step 1: Group Versions by Article
- Add **Aggregate** node:
  - Aggregate by: article_id
  - This creates one item per article containing all 3 model versions

#### Step 2: Prepare Comparison Prompt
- Add **Function** node:
```javascript
const article = $input.item(0).json;
const versions = article.items; // All 3 model outputs

// Extract versions for each format
const headlineVersions = versions.map(v => ({
  model: v.model,
  content: v.generated_content.headline
})).filter(v => v.content);

const carouselVersions = versions.map(v => ({
  model: v.model,
  content: v.generated_content.carousel
})).filter(v => v.content);

const videoVersions = versions.map(v => ({
  model: v.model,
  content: v.generated_content.video
})).filter(v => v.content);

const podcastVersions = versions.map(v => ({
  model: v.model,
  content: v.generated_content.podcast
})).filter(v => v.content);

return [{
  json: {
    article_id: article.article_id,
    prompt: `You are a content quality judge. Compare these versions and pick the BEST one for each format.

EVALUATION CRITERIA:
- Engagement: Will this capture attention?
- Clarity: Is the message clear?
- Slovak language quality: Natural, culturally appropriate
- Virality potential: Shareable, memorable
- Format optimization: Does it use the format well?

HEADLINE VERSIONS:
${JSON.stringify(headlineVersions, null, 2)}

CAROUSEL VERSIONS:
${JSON.stringify(carouselVersions, null, 2)}

VIDEO VERSIONS:
${JSON.stringify(videoVersions, null, 2)}

PODCAST VERSIONS:
${JSON.stringify(podcastVersions, null, 2)}

RETURN JSON ONLY:
{
  "headline_winner": "<model_name>",
  "headline_reasoning": "...",
  "carousel_winner": "<model_name>",
  "carousel_reasoning": "...",
  "video_winner": "<model_name>",
  "video_reasoning": "...",
  "podcast_winner": "<model_name>",
  "podcast_reasoning": "..."
}`
  }
}];
```

#### Step 3: Run Second Judge
- Add **OpenAI** node:
  - Model: gpt-5
  - System Message: "You are an expert content quality evaluator. Always respond with valid JSON."
  - User Message: `{{ $json.prompt }}`
  - Temperature: 0.2 (consistent, objective judging)
  - Max Tokens: 1000
  - Response Format: JSON Object

#### Step 4: Extract Winners
- Add **Function** node:
```javascript
const items = $input.all();
return items.map(item => {
  const judgment = JSON.parse(item.json.choices[0].message.content);
  const versions = item.json.versions;
  
  // Find winning content for each format
  const headlineWinner = versions.find(v => 
    v.model === judgment.headline_winner
  )?.generated_content.headline;
  
  const carouselWinner = versions.find(v => 
    v.model === judgment.carousel_winner
  )?.generated_content.carousel;
  
  const videoWinner = versions.find(v => 
    v.model === judgment.video_winner
  )?.generated_content.video;
  
  const podcastWinner = versions.find(v => 
    v.model === judgment.podcast_winner
  )?.generated_content.podcast;
  
  return {
    json: {
      article_id: item.json.article_id,
      winning_content: {
        headline: headlineWinner,
        carousel: carouselWinner,
        video: videoWinner,
        podcast: podcastWinner
      },
      winning_models: {
        headline: judgment.headline_winner,
        carousel: judgment.carousel_winner,
        video: judgment.video_winner,
        podcast: judgment.podcast_winner
      }
    }
  };
});
```

#### Step 5: Update Model Performance Tracking
- Add **Postgres** node (runs for each winning model):
```sql
INSERT INTO model_performance (model_name, content_type, judge_wins, total_posts)
VALUES ($1, $2, 1, 1)
ON CONFLICT (model_name, content_type) 
DO UPDATE SET 
  judge_wins = model_performance.judge_wins + 1,
  total_posts = model_performance.total_posts + 1,
  last_updated = NOW();
```
- Parameters: model_name, content_type (headline/carousel/video/podcast)

#### Step 6: Store Winning Content
- Add **Function** node to prepare for database:
```javascript
const items = $input.all();
const posts = [];

items.forEach(item => {
  const formats = ['headline', 'carousel', 'video', 'podcast'];
  
  formats.forEach(format => {
    if (item.json.winning_content[format]) {
      posts.push({
        article_id: item.json.article_id,
        content_type: format,
        generating_model: item.json.winning_models[format],
        content: item.json.winning_content[format]
      });
    }
  });
});

return posts.map(p => ({ json: p }));
```

- Add **Supabase** node:
  - Operation: Insert
  - Table: posts
  - Data: From Function node
  - Return Fields: id, article_id, content_type

### Testing Checklist
- [ ] Versions grouped by article correctly
- [ ] Judge compares all formats
- [ ] Winners selected logically
- [ ] Model performance tracking updates
- [ ] Winning content stored in database
- [ ] All format types handled

---

## 7. Media Creation Module

### Purpose
Generate/gather images, create videos, generate audio for content.

### Sub-Components
1. **Image Acquisition** (article images or AI generation)
2. **Video Creation** (slideshow + voiceover + captions + music)
3. **Audio Generation** (podcast voiceover)
4. **Text Overlay** (headlines on images)

### n8n Nodes Required
- **HTTP Request** node (image scraping, DALL-E API)
- **OpenAI** node (DALL-E image generation)
- **HTTP Request** node (ElevenLabs TTS)
- **Code** node (FFmpeg for video creation, image manipulation)
- **Function** nodes (data prep)

### Implementation Steps

---

### 7A. Image Acquisition

#### Step 1: Extract Images from Articles
- Add **Function** node:
```javascript
// Parse article HTML to find images
const article = $input.item(0).json;
const content = article.content;

// Simple regex to find img tags (adjust for actual HTML structure)
const imgRegex = /<img[^>]+src="([^">]+)"/g;
const images = [];
let match;

while ((match = imgRegex.exec(content)) !== null) {
  images.push(match[1]);
}

return [{
  json: {
    article_id: article.article_id,
    found_images: images,
    needs_ai_generation: images.length === 0
  }
}];
```

#### Step 2: Download Article Images (if available)
- Add **IF** node: Check if `found_images.length > 0`
- If TRUE, add **HTTP Request** node:
  - Method: GET
  - URL: `{{ $json.found_images[0] }}` (get first/best image)
  - Response Format: File
  - Download: Yes
  - Binary Property: image_data

#### Step 3: AI Image Generation (fallback)
- If FALSE (no images found), add **OpenAI** node:
  - Operation: Generate an Image (DALL-E)
  - Prompt: 
```javascript
`Create a dramatic, eye-catching image for this Slovak celebrity news story: ${$json.article_title}. Style: modern, bold, news-worthy, attention-grabbing. No text in image.`
```
  - Size: 1024x1024 (Instagram square)
  - Quality: Standard (cheaper)
  - Response Format: URL
  
- Add **HTTP Request** node to download generated image:
  - URL: `{{ $json.data[0].url }}`
  - Download: Yes
  - Binary Property: image_data

#### Step 4: Store Image Reference
- Add **Function** node:
```javascript
return [{
  json: {
    article_id: $json.article_id,
    image_source: $json.needs_ai_generation ? 'ai_generated' : 'article_image',
    image_url: $json.image_url, // or path to downloaded file
    binary_data: $binary.image_data
  }
}];
```

---

### 7B. Text Overlay on Images

**For MVP:** Using Code node with Node.js canvas library

#### Step 1: Install Dependencies
In your n8n environment:
```bash
npm install canvas
```

#### Step 2: Add Text to Image
- Add **Code** node (JavaScript):
```javascript
const { createCanvas, loadImage } = require('canvas');

const items = $input.all();
const results = [];

for (const item of items) {
  const imageBuffer = item.binary.image_data.data;
  const headline = item.json.content.headline;
  
  // Load image
  const image = await loadImage(imageBuffer);
  
  // Create canvas
  const canvas = createCanvas(image.width, image.height);
  const ctx = canvas.getContext('2d');
  
  // Draw original image
  ctx.drawImage(image, 0, 0);
  
  // Add semi-transparent overlay for text readability
  ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
  ctx.fillRect(0, image.height - 200, image.width, 200);
  
  // Add headline text
  ctx.fillStyle = '#FFFFFF';
  ctx.font = 'bold 48px Arial';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  
  // Wrap text if too long
  const maxWidth = image.width - 40;
  const words = headline.split(' ');
  let line = '';
  let y = image.height - 120;
  
  for (const word of words) {
    const testLine = line + word + ' ';
    const metrics = ctx.measureText(testLine);
    if (metrics.width > maxWidth && line !== '') {
      ctx.fillText(line, image.width / 2, y);
      line = word + ' ';
      y += 60;
    } else {
      line = testLine;
    }
  }
  ctx.fillText(line, image.width / 2, y);
  
  // Convert to buffer
  const outputBuffer = canvas.toBuffer('image/jpeg');
  
  results.push({
    json: {
      article_id: item.json.article_id,
      content_type: 'headline_image'
    },
    binary: {
      final_image: {
        data: outputBuffer,
        mimeType: 'image/jpeg',
        fileName: `headline_${item.json.article_id}.jpg`
      }
    }
  });
}

return results;
```

---

### 7C. Video Creation (TikTok/Reels)

#### Step 1: Gather Video Components
- Video script (from winning content)
- Images (3-7 images per video)
- Background music mood
- Duration

#### Step 2: Generate Voiceover (ElevenLabs)
- Add **HTTP Request** node:
  - Method: POST
  - URL: `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
  - Authentication: API Key
  - Headers:
    ```json
    {
      "xi-api-key": "YOUR_ELEVENLABS_API_KEY",
      "Content-Type": "application/json"
    }
    ```
  - Body (JSON):
```javascript
{
  "text": "{{ $json.content.video.script }}",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.75
  }
}
```
  - Response Format: File
  - Binary Property: voiceover_audio

**Voice IDs for Slovak:**
- Male (20s-30s): Use voice_id from ElevenLabs voice library
- Female (20s-30s): Use voice_id from ElevenLabs voice library
- You'll need to browse their voice library and select appropriate Slovak-sounding voices

#### Step 3: Generate Captions (Whisper for timing)
- Add **HTTP Request** node (OpenAI Whisper):
  - Method: POST
  - URL: `https://api.openai.com/v1/audio/transcriptions`
  - Body: audio file + parameters
  - Response format: SRT (with timestamps)
  - Language: sk (Slovak)

#### Step 4: Select Background Music
- Add **Function** node:
```javascript
// Map mood to music file
const mood = $json.content.video.background_music_mood;

const musicLibrary = {
  'upbeat': '/music/upbeat_01.mp3',
  'dramatic': '/music/dramatic_01.mp3',
  'sad': '/music/sad_01.mp3',
  'chill': '/music/chill_01.mp3',
  'energetic': '/music/energetic_01.mp3'
};

return [{
  json: {
    article_id: $json.article_id,
    music_path: musicLibrary[mood] || musicLibrary['upbeat']
  }
}];
```

**Note:** You'll need to pre-populate a library of royalty-free music files organized by mood.

#### Step 5: Combine into Video (FFmpeg)
- Add **Code** node (JavaScript with FFmpeg):
```javascript
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
const fs = require('fs').promises;

const items = $input.all();
const results = [];

for (const item of items) {
  const images = item.json.images; // Array of image paths
  const audioPath = '/tmp/voiceover.mp3';
  const musicPath = item.json.music_path;
  const srtPath = '/tmp/captions.srt';
  const outputPath = `/tmp/video_${item.json.article_id}.mp4`;
  
  // Save audio to temp file
  await fs.writeFile(audioPath, item.binary.voiceover_audio.data);
  
  // Save SRT captions
  await fs.writeFile(srtPath, item.json.captions);
  
  // Create image list for slideshow
  const imageListPath = '/tmp/images.txt';
  const imageList = images.map((img, i) => 
    `file '${img}'\nduration ${item.json.content.video.duration_seconds / images.length}`
  ).join('\n');
  await fs.writeFile(imageListPath, imageList);
  
  // FFmpeg command to create video
  const ffmpegCmd = `
    ffmpeg -f concat -safe 0 -i ${imageListPath} \
    -i ${audioPath} \
    -i ${musicPath} \
    -filter_complex "[1:a]volume=1.0[a1];[2:a]volume=0.3[a2];[a1][a2]amix=inputs=2:duration=first[audio];[0:v]subtitles=${srtPath}:force_style='Fontsize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Bold=1,Alignment=2'[v]" \
    -map "[v]" -map "[audio]" \
    -c:v libx264 -preset fast -crf 23 \
    -c:a aac -b:a 192k \
    -shortest \
    ${outputPath}
  `;
  
  await execAsync(ffmpegCmd);
  
  // Read output video
  const videoBuffer = await fs.readFile(outputPath);
  
  results.push({
    json: {
      article_id: item.json.article_id,
      content_type: 'video',
      platform: 'tiktok' // or 'reels'
    },
    binary: {
      video_file: {
        data: videoBuffer,
        mimeType: 'video/mp4',
        fileName: `video_${item.json.article_id}.mp4`
      }
    }
  });
  
  // Cleanup temp files
  await fs.unlink(audioPath);
  await fs.unlink(srtPath);
  await fs.unlink(imageListPath);
  await fs.unlink(outputPath);
}

return results;
```

**Important:** This requires FFmpeg installed in your n8n environment:
```bash
apt-get install ffmpeg
```

---

### 7D. Podcast Audio Generation

#### Step 1: Batch High-Scoring Articles for Podcast
- Add **Aggregate** node:
  - Aggregate by: None (collect all)
  - Filter: content_type = 'podcast' AND judge_score >= 8
  - Wait for: 5 items (5 articles for one podcast episode)

#### Step 2: Combine Scripts
- Add **Function** node:
```javascript
const articles = $input.all();

// Sort by score (best first)
articles.sort((a, b) => b.json.judge_score - a.json.judge_score);

// Take top 5
const top5 = articles.slice(0, 5);

// Combine dialogues with transitions
let fullScript = [];

// Opening
fullScript.push({
  speaker: "Male",
  text: "Ahoj! Vitajte pri dnešnom prehľade najhorúcejších slovenských celebrity správ!"
});

fullScript.push({
  speaker: "Female",
  text: "Mám tu päť príbehov, ktoré rozhodne musíte počuť. Začnime!"
});

// Add each article's dialogue
top5.forEach((article, index) => {
  // Transition
  if (index > 0) {
    fullScript.push({
      speaker: "Male",
      text: "A čo ďalej?"
    });
  }
  
  // Add article dialogue
  fullScript.push(...article.json.content.podcast.dialogue);
});

// Closing
fullScript.push({
  speaker: "Female",
  text: "To je všetko na dnes. Ďakujeme za počúvanie!"
});

fullScript.push({
  speaker: "Male",
  text: "Nezabudnite sa prihlásiť k odberu. Dovidenia!"
});

return [{
  json: {
    podcast_id: `podcast_${Date.now()}`,
    full_script: fullScript,
    article_ids: top5.map(a => a.json.article_id)
  }
}];
```

#### Step 3: Generate Audio for Each Speaker Turn
- Add **SplitInBatches** node (process each line)
- Add **Function** node to determine voice:
```javascript
const voiceIds = {
  "Male": "YOUR_MALE_VOICE_ID", // From ElevenLabs
  "Female": "YOUR_FEMALE_VOICE_ID" // From ElevenLabs
};

return [{
  json: {
    text: $json.text,
    voice_id: voiceIds[$json.speaker],
    speaker: $json.speaker
  }
}];
```

- Add **HTTP Request** node (ElevenLabs):
  - Same as video voiceover
  - Store each audio segment

#### Step 4: Concatenate Audio Segments
- Add **Code** node:
```javascript
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);
const fs = require('fs').promises;

const items = $input.all();
const podcast_id = items[0].json.podcast_id;

// Save all audio segments
const segmentPaths = [];
for (let i = 0; i < items.length; i++) {
  const path = `/tmp/segment_${i}.mp3`;
  await fs.writeFile(path, items[i].binary.audio_segment.data);
  segmentPaths.push(path);
}

// Create concat list
const concatList = segmentPaths.map(p => `file '${p}'`).join('\n');
const listPath = '/tmp/concat_list.txt';
await fs.writeFile(listPath, concatList);

// Concatenate with FFmpeg
const outputPath = `/tmp/podcast_${podcast_id}.mp3`;
await execAsync(`ffmpeg -f concat -safe 0 -i ${listPath} -c copy ${outputPath}`);

// Read final podcast
const podcastBuffer = await fs.readFile(outputPath);

// Cleanup
for (const path of segmentPaths) {
  await fs.unlink(path);
}
await fs.unlink(listPath);
await fs.unlink(outputPath);

return [{
  json: {
    podcast_id: podcast_id
  },
  binary: {
    podcast_audio: {
      data: podcastBuffer,
      mimeType: 'audio/mpeg',
      fileName: `podcast_${podcast_id}.mp3`
    }
  }
}];
```

#### Step 5: Create YouTube Video from Podcast
For YouTube, combine podcast audio with slideshow:
- Reuse images from the 5 articles
- Create slideshow video (similar to TikTok process)
- Use podcast audio as voiceover
- Add simple visualizer or static image

### Testing Checklist
- [ ] Images extracted/generated successfully
- [ ] Text overlay readable and positioned well
- [ ] Videos created with correct timing
- [ ] Captions synced to voiceover
- [ ] Background music at appropriate volume
- [ ] Podcast segments concatenated smoothly
- [ ] YouTube video format correct
- [ ] All media files stored/referenced properly

---

## 8. Publishing Module

### Purpose
Post content to social media platforms with rate limiting and smart scheduling.

### Platforms & Posting Methods
- **Instagram:** Graph API (Business account required)
- **Facebook:** Graph API (Page required)
- **TikTok:** Manual upload for MVP (API requires business approval)
- **YouTube:** YouTube Data API

### Rate Limits (per platform)
- Instagram: 5-6 posts/day, 3-4 hours apart
- Facebook: 5-6 posts/day, 3-4 hours apart
- TikTok: 8-10 posts/day, 2-3 hours apart (when API available)
- YouTube: 2-3 videos/day

### Smart Scheduling
- Active hours: 7 AM - 11 PM
- Posting windows: 7 AM, 10 AM, 1 PM, 4 PM, 7 PM, 10 PM
- Each window can post 3-5 pieces across platforms

### n8n Nodes Required
- **HTTP Request** nodes (API calls)
- **Schedule Trigger** node (posting windows)
- **Supabase** node (queue management)
- **IF** nodes (conditional posting)
- **Function** nodes (data prep)

### Implementation Steps

---

### 8A. Post Queue Management

#### Step 1: Create Posting Queue
- Add **Supabase** node:
  - Operation: Get Many
  - Table: posts
  - Filters:
    - posted_at IS NULL (not yet posted)
    - created_at > NOW() - INTERVAL '24 hours'
  - Sort: judge_score DESC (best content first)
  - Limit: 50

#### Step 2: Schedule Trigger for Posting Windows
- Add **Schedule Trigger** node:
  - Cron: `0 7,10,13,16,19,22 * * *` (6 times daily)
  - This triggers at: 7am, 10am, 1pm, 4pm, 7pm, 10pm

#### Step 3: Determine Posts for This Window
- Add **Function** node:
```javascript
const queue = $input.all();
const now = new Date();

// Calculate posts per platform for this window
const postsPerPlatform = {
  instagram: 1, // 1 post every 3 hours = 6/day max
  facebook: 1,
  youtube: Math.floor(Math.random() * 2) === 0 ? 1 : 0 // Occasionally (2-3/day)
};

// Select posts for each platform
const selectedPosts = {
  instagram: [],
  facebook: [],
  youtube: []
};

// Prioritize by content type and score
const headlines = queue.filter(p => p.json.content_type === 'headline_image');
const carousels = queue.filter(p => p.json.content_type === 'carousel');
const videos = queue.filter(p => p.json.content_type === 'video');
const podcasts = queue.filter(p => p.json.content_type === 'podcast');

// Instagram: Mix of headlines, carousels, videos
if (postsPerPlatform.instagram > 0) {
  if (carousels.length > 0) {
    selectedPosts.instagram.push(carousels[0]);
  } else if (videos.length > 0) {
    selectedPosts.instagram.push(videos[0]);
  } else if (headlines.length > 0) {
    selectedPosts.instagram.push(headlines[0]);
  }
}

// Facebook: Similar strategy
if (postsPerPlatform.facebook > 0) {
  const fbContent = [...headlines, ...carousels].filter(
    p => !selectedPosts.instagram.includes(p)
  );
  if (fbContent.length > 0) {
    selectedPosts.facebook.push(fbContent[0]);
  }
}

// YouTube: Podcasts only
if (postsPerPlatform.youtube > 0 && podcasts.length > 0) {
  selectedPosts.youtube.push(podcasts[0]);
}

return Object.entries(selectedPosts).flatMap(([platform, posts]) =>
  posts.map(post => ({
    json: {
      ...post.json,
      target_platform: platform
    },
    binary: post.binary
  }))
);
```

---

### 8B. Instagram Posting

**Prerequisites:**
- Instagram Business Account
- Facebook Page connected to Instagram
- Facebook App with Instagram Basic Display API
- Access Token

#### Step 1: Filter for Instagram Posts
- Add **IF** node:
  - Condition: `{{ $json.target_platform }}` equals "instagram"

#### Step 2: Prepare Instagram Post Data
- Add **Function** node:
```javascript
const post = $input.item(0).json;
const contentType = post.content_type;

let postData = {
  access_token: 'YOUR_FB_ACCESS_TOKEN',
  caption: ''
};

if (contentType === 'headline_image') {
  postData.caption = post.content.headline;
  postData.image_url = post.media_urls[0]; // Assuming image uploaded to public URL
} else if (contentType === 'carousel') {
  postData.caption = post.content.carousel[0]; // First slide as caption
  postData.media_type = 'CAROUSEL';
  postData.children = post.media_urls.map(url => ({
    media_type: 'IMAGE',
    image_url: url
  }));
} else if (contentType === 'video') {
  postData.caption = post.content.video.script.substring(0, 200); // Truncate
  postData.media_type = 'REELS';
  postData.video_url = post.media_urls[0];
}

return [{ json: postData }];
```

#### Step 3: Create Instagram Container
- Add **HTTP Request** node:
  - Method: POST
  - URL: `https://graph.facebook.com/v18.0/{instagram-account-id}/media`
  - Body (JSON): `{{ $json }}`
  - Response: Extract `id` (container ID)

#### Step 4: Publish Container
- Add **HTTP Request** node:
  - Method: POST
  - URL: `https://graph.facebook.com/v18.0/{instagram-account-id}/media_publish`
  - Body:
```json
{
  "creation_id": "{{ $json.id }}",
  "access_token": "YOUR_FB_ACCESS_TOKEN"
}
```
  - Response: Extract post `id` and `permalink`

#### Step 5: Update Database
- Add **Supabase** node:
  - Operation: Update
  - Table: posts
  - Update Key: id
  - Data:
    - posted_at = NOW()
    - platform = 'instagram'
    - post_url = {{ $json.permalink }}

#### Step 6: Error Handling
- Add **Error Trigger** node after Instagram posting
- If error occurs:
  - Retry count check (max 3)
  - If retry < 3: Wait 5 minutes, retry
  - If retry = 3: Log error, move to manual queue

---

### 8C. Facebook Posting

#### Step 1: Filter for Facebook Posts
- Add **IF** node:
  - Condition: `{{ $json.target_platform }}` equals "facebook"

#### Step 2: Post to Facebook Page
- Add **HTTP Request** node:
  - Method: POST
  - URL: `https://graph.facebook.com/v18.0/{page-id}/photos` (for images)
    - OR `https://graph.facebook.com/v18.0/{page-id}/videos` (for videos)
  - Body (form-data or JSON):
```json
{
  "message": "{{ $json.content.headline || $json.content.carousel[0] }}",
  "url": "{{ $json.media_urls[0] }}", // For photos
  // OR "file_url": for videos
  "access_token": "YOUR_PAGE_ACCESS_TOKEN"
}
```

#### Step 3: Update Database
- Same as Instagram (Step 5)

---

### 8D. YouTube Posting

#### Step 1: Filter for YouTube Posts
- Add **IF** node:
  - Condition: `{{ $json.target_platform }}` equals "youtube"

#### Step 2: Upload Video
- Add **HTTP Request** node:
  - Method: POST
  - URL: `https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status`
  - Authentication: OAuth2 (YouTube Data API)
  - Body (multipart):
```json
{
  "snippet": {
    "title": "{{ $json.content.video.script.substring(0, 100) }}",
    "description": "Denný prehľad slovenských celebrity správ",
    "tags": ["celebrity", "gossip", "slovensko", "news"],
    "categoryId": "24" // Entertainment
  },
  "status": {
    "privacyStatus": "public"
  }
}
```
  - Include video file as binary data

#### Step 3: Update Database
- Same as Instagram

---

### 8E. TikTok (Manual Upload for MVP)

#### Step 1: Export to Folder
Since TikTok API requires business approval, use manual workflow for MVP:

- Add **IF** node:
  - Condition: content_type = 'video' AND target would be TikTok

- Add **Google Drive** node (or similar):
  - Operation: Upload
  - Folder: "TikTok Ready"
  - File: `{{ $binary.video_file }}`
  - Filename: `tiktok_{{ $json.article_id }}.mp4`

- Add **Discord** webhook (notification):
  - Message: "New TikTok video ready! Check Google Drive > TikTok Ready folder"
  - Include caption: `{{ $json.content.video.script.substring(0, 100) }}`

#### Step 2: Mark as "Manual Upload Needed"
- Add **Supabase** node:
  - Update post record
  - Set status = 'pending_manual_upload'

**Future:** Once TikTok business API approved, replace with API posting similar to Instagram.

---

### 8F. Rate Limit Enforcement

#### Global Rate Limiter Function
Add this at the start of posting module:

- Add **Function** node:
```javascript
const platform = $json.target_platform;
const now = new Date();
const hour = now.getHours();

// Define rate limits
const rateLimits = {
  instagram: { max_per_window: 1, hours_between: 3 },
  facebook: { max_per_window: 1, hours_between: 3 },
  youtube: { max_per_day: 3 }
};

// Query recent posts from Supabase (done in previous node)
const recentPosts = $node["GetRecentPosts"].json;

// Check if can post
const platformPosts = recentPosts.filter(p => 
  p.platform === platform &&
  new Date(p.posted_at) > new Date(now - rateLimits[platform].hours_between * 3600000)
);

const canPost = platformPosts.length < rateLimits[platform].max_per_window;

return [{
  json: {
    can_post: canPost,
    reason: canPost ? 'OK' : `Rate limit: ${platformPosts.length} posts in last ${rateLimits[platform].hours_between}hrs`
  }
}];
```

- Add **IF** node:
  - If can_post = true: Continue to posting
  - If can_post = false: Log and skip

### Testing Checklist
- [ ] Schedule triggers at correct times
- [ ] Queue filtered properly
- [ ] Instagram posts successfully
- [ ] Facebook posts successfully
- [ ] YouTube uploads successfully
- [ ] TikTok videos exported for manual upload
- [ ] Rate limits enforced
- [ ] Database updated after posting
- [ ] Errors handled gracefully
- [ ] Notifications sent

---

## 9. Performance Tracking Module

### Purpose
Measure post engagement at multiple checkpoints, store metrics, feed back to judging system.

### Checkpoints
- 1 hour after posting
- 6 hours after posting
- 24 hours after posting

### Metrics to Track
- Likes
- Comments
- Shares
- Views (for videos)
- Engagement rate: `(likes + comments + shares) / followers * 100`

### n8n Nodes Required
- **Schedule Trigger** nodes (checkpoint timers)
- **Supabase** node (query posts to check)
- **HTTP Request** nodes (platform APIs)
- **Function** nodes (calculations)
- **Postgres** node (aggregations)

### Implementation Steps

#### Step 1: Schedule Checkpoint Triggers
Create 3 separate workflows (or branches):

**1-Hour Checkpoint:**
- Add **Schedule Trigger**:
  - Cron: `0 * * * *` (every hour)
  
**6-Hour Checkpoint:**
- Add **Schedule Trigger**:
  - Cron: `0 */6 * * *` (every 6 hours)

**24-Hour Checkpoint:**
- Add **Schedule Trigger**:
  - Cron: `0 8 * * *` (daily at 8 AM)

#### Step 2: Find Posts to Check
For each checkpoint, query posts that need metrics:

- Add **Supabase** node:
  - Operation: Get Many
  - Table: posts
  - Filters (example for 1hr checkpoint):
    - posted_at BETWEEN (NOW() - INTERVAL '1 hour 10 minutes') AND (NOW() - INTERVAL '50 minutes')
    - posted_at IS NOT NULL
  - This finds posts published approximately 1 hour ago

#### Step 3: Fetch Instagram Metrics
- Add **IF** node: Filter platform = 'instagram'
- Add **HTTP Request** node:
  - Method: GET
  - URL: `https://graph.facebook.com/v18.0/{post-id}?fields=like_count,comments_count,shares_count,insights.metric(impressions,reach)&access_token=YOUR_TOKEN`
  - Response: JSON with metrics

- Add **Function** node:
```javascript
const response = $input.item(0).json;

return [{
  json: {
    post_id: $json.post_id,
    checkpoint: '1hr',
    likes: response.like_count || 0,
    comments: response.comments_count || 0,
    shares: response.shares_count || 0,
    views: response.insights?.data[0]?.values[0]?.value || 0,
    engagement_rate: calculateEngagementRate(response)
  }
}];

function calculateEngagementRate(data) {
  const total_engagement = (data.like_count || 0) + (data.comments_count || 0) + (data.shares_count || 0);
  const reach = data.insights?.data[0]?.values[0]?.value || 1;
  return (total_engagement / reach * 100).toFixed(2);
}
```

#### Step 4: Fetch Facebook Metrics
- Add **IF** node: Filter platform = 'facebook'
- Add **HTTP Request** node:
  - Similar to Instagram
  - URL: `https://graph.facebook.com/v18.0/{post-id}?fields=reactions.summary(total_count),comments.summary(total_count),shares&access_token=YOUR_TOKEN`

#### Step 5: Fetch YouTube Metrics
- Add **IF** node: Filter platform = 'youtube'
- Add **HTTP Request** node:
  - Method: GET
  - URL: `https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video-id}&key=YOUR_API_KEY`
  - Response includes: viewCount, likeCount, commentCount

#### Step 6: Store Metrics
- Add **Merge** node: Combine all platform metrics
- Add **Supabase** node:
  - Operation: Insert
  - Table: performance_metrics
  - Data:
    - post_id
    - checked_at = NOW()
    - checkpoint ('1hr', '6hr', '24hr')
    - likes, comments, shares, views
    - engagement_rate

#### Step 7: Update Model Performance (24hr checkpoint only)
After 24hr metrics collected:

- Add **Postgres** node:
```sql
WITH post_performance AS (
  SELECT 
    p.generating_model,
    p.content_type,
    AVG(pm.engagement_rate) as avg_engagement
  FROM posts p
  JOIN performance_metrics pm ON p.id = pm.post_id
  WHERE pm.checkpoint = '24hr'
  AND pm.checked_at > NOW() - INTERVAL '7 days'
  GROUP BY p.generating_model, p.content_type
)
UPDATE model_performance mp
SET 
  avg_engagement = pp.avg_engagement,
  last_updated = NOW()
FROM post_performance pp
WHERE mp.model_name = pp.generating_model
AND mp.content_type = pp.content_type;
```

#### Step 8: Analyze Trending Topics/Keywords
Weekly analysis (separate workflow):

- Add **Schedule Trigger**: Weekly (Monday 9 AM)
- Add **Postgres** node:
```sql
SELECT 
  p.content->>'topic' as topic,
  COUNT(*) as post_count,
  AVG(pm.engagement_rate) as avg_engagement,
  SUM(pm.likes + pm.comments + pm.shares) as total_engagement
FROM posts p
JOIN performance_metrics pm ON p.id = pm.post_id
WHERE pm.checkpoint = '24hr'
AND pm.checked_at > NOW() - INTERVAL '7 days'
GROUP BY topic
ORDER BY avg_engagement DESC
LIMIT 20;
```

- Store results for First Judge feedback loop (used in Component 4)

### Testing Checklist
- [ ] Checkpoint triggers fire at correct times
- [ ] Posts correctly identified for each checkpoint
- [ ] Instagram metrics fetched successfully
- [ ] Facebook metrics fetched successfully
- [ ] YouTube metrics fetched successfully
- [ ] Metrics stored in database
- [ ] Model performance updated after 24hr
- [ ] Trending topics calculated weekly
- [ ] Engagement rates calculated correctly

---

## Configuration & Settings

### API Keys & Credentials Required

#### AI/ML Services
- **OpenAI API Key**
  - For: GPT-5, GPT-5 Mini, GPT-5 Nano, DALL-E, Whisper
  - Get from: https://platform.openai.com/api-keys
  - Cost: Pay-as-you-go

- **Anthropic API Key**
  - For: Claude Haiku 4.5
  - Get from: https://console.anthropic.com/
  - Cost: Pay-as-you-go

- **Google AI API Key**
  - For: Gemini 2.5 Flash
  - Get from: https://aistudio.google.com/
  - Cost: Free tier available, then pay-as-you-go

- **ElevenLabs API Key**
  - For: Voice synthesis (podcasts, videos)
  - Get from: https://elevenlabs.io/
  - Cost: ~$22/month for 100k characters (~70 minutes audio)

#### Database
- **Supabase**
  - Project URL
  - API Key (anon/service role)
  - Database password
  - Get from: https://supabase.com/ (free tier: 500MB database, 2GB bandwidth)

#### Social Media Platforms
- **Facebook/Instagram**
  - Facebook App ID
  - Facebook App Secret
  - Page Access Token (long-lived)
  - Instagram Business Account ID
  - Setup: https://developers.facebook.com/

- **YouTube**
  - Google Cloud Project
  - OAuth 2.0 Client ID
  - OAuth 2.0 Client Secret
  - Setup: https://console.cloud.google.com/

- **TikTok** (future)
  - TikTok Developer Account
  - App credentials
  - Business account approval required

#### Monitoring
- **Discord Webhook URL**
  - For error/queue notifications
  - Create webhook in Discord server settings

### Environment Variables (n8n)
Set these in your n8n environment:

```bash
# AI Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...
ELEVENLABS_API_KEY=...

# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
SUPABASE_PASSWORD=...

# Social Media
FB_APP_ID=...
FB_APP_SECRET=...
FB_PAGE_ACCESS_TOKEN=...
INSTAGRAM_ACCOUNT_ID=...
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...

# Monitoring
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Queue Thresholds
QUEUE_THRESHOLD_LOW=20
QUEUE_THRESHOLD_MEDIUM=40
QUEUE_THRESHOLD_HIGH=60

# Rate Limits
INSTAGRAM_MAX_PER_WINDOW=1
INSTAGRAM_HOURS_BETWEEN=3
FACEBOOK_MAX_PER_WINDOW=1
FACEBOOK_HOURS_BETWEEN=3
YOUTUBE_MAX_PER_DAY=3
```

### Model Selection Configuration

Create a configuration node/file for easy swapping:

```javascript
const modelConfig = {
  extraction: {
    model: "gpt-5-nano",
    provider: "openai",
    temperature: 0.1,
    max_tokens: 1000
  },
  
  first_judge: {
    model: "gpt-5",
    provider: "openai",
    temperature: 0.3,
    max_tokens: 500
  },
  
  generators: [
    {
      model: "gpt-5-mini",
      provider: "openai",
      temperature: 0.7,
      max_tokens: 2000
    },
    {
      model: "claude-haiku-4-5",
      provider: "anthropic",
      temperature: 0.7,
      max_tokens: 2000
    },
    {
      model: "gemini-2.5-flash",
      provider: "google",
      temperature: 0.7,
      max_tokens: 2000
    }
  ],
  
  second_judge: {
    model: "gpt-5",
    provider: "openai",
    temperature: 0.2,
    max_tokens: 1000
  }
};
```

### Content Format Rules

```javascript
const formatRules = {
  scoring: {
    podcast: { min_score: 8 },
    video: { min_score: 8 },
    carousel: { min_score: 6 },
    headline: { min_score: 4 }
  },
  
  character_limits: {
    headline: 140,
    carousel_slide: 140,
    video_caption: 200,
    podcast_segment: 2000 // characters
  },
  
  carousel: {
    min_slides: 3,
    max_slides: 8
  },
  
  video: {
    min_duration: 10, // seconds
    max_duration: 120,
    caption_font_size: 24,
    caption_position: "bottom"
  },
  
  podcast: {
    articles_per_episode: 5,
    max_duration: 300 // 5 minutes
  }
};
```

### Scheduling Configuration

```javascript
const scheduleConfig = {
  scraping: {
    cron: "0 * * * *", // Every hour
    timezone: "Europe/Bratislava"
  },
  
  posting_windows: {
    cron: "0 7,10,13,16,19,22 * * *", // 6 times daily
    active_hours: { start: 7, end: 23 }, // 7 AM - 11 PM
    timezone: "Europe/Bratislava"
  },
  
  performance_tracking: {
    checkpoint_1hr: "0 * * * *",
    checkpoint_6hr: "0 */6 * * *",
    checkpoint_24hr: "0 8 * * *" // 8 AM daily
  },
  
  maintenance: {
    delete_old_articles: "0 3 * * *", // 3 AM daily
    weekly_analysis: "0 9 * * 1" // Monday 9 AM
  }
};
```

---

## Error Handling & Monitoring

### Error Categories & Responses

#### 1. Scraping Errors
**Error:** Website down/unreachable
- **Response:** Continue with remaining sources
- **Retry:** No immediate retry
- **Alert:** Only if all sources fail
- **Log:** Store in error_log table

**Error:** HTML parsing fails
- **Response:** Skip article, continue
- **Retry:** No
- **Alert:** No (expected occasional failures)

#### 2. API Errors (AI Models)
**Error:** Rate limit exceeded
- **Response:** Wait 60 seconds, retry
- **Retry:** Max 3 attempts with exponential backoff (1min, 2min, 4min)
- **Alert:** After 3 failures
- **Log:** Yes

**Error:** Model timeout
- **Response:** Retry immediately
- **Retry:** Max 2 attempts
- **Alert:** After 2 failures

**Error:** Invalid response/JSON parsing
- **Response:** Log error, mark article as failed
- **Retry:** No (likely prompt issue)
- **Alert:** Yes (needs prompt review)

#### 3. Social Media Posting Errors
**Error:** Post rejected (content policy)
- **Response:** Mark as failed, don't retry
- **Alert:** Yes (manual review needed)
- **Log:** Store full error message

**Error:** Authentication expired
- **Response:** Pause posting, alert immediately
- **Retry:** No automatic retry
- **Alert:** HIGH PRIORITY - needs token refresh

**Error:** Rate limit
- **Response:** Queue post for later window
- **Retry:** Next posting window
- **Alert:** No

#### 4. Database Errors
**Error:** Connection lost
- **Response:** Retry connection with exponential backoff
- **Retry:** Max 5 attempts (5s, 10s, 20s, 40s, 80s)
- **Alert:** After 5 failures (critical)

**Error:** Constraint violation (duplicate)
- **Response:** Skip insertion, continue
- **Retry:** No
- **Alert:** No

### Error Workflow Implementation

#### Global Error Handler
Add **Error Trigger** node at workflow level:

```javascript
const error = $input.item(0).json.error;
const nodeName = $json.node.name;
const workflowName = $workflow.name;

// Categorize error
let severity = 'LOW';
let shouldAlert = false;
let shouldRetry = false;

if (error.message.includes('rate limit')) {
  severity = 'MEDIUM';
  shouldRetry = true;
} else if (error.message.includes('authentication')) {
  severity = 'HIGH';
  shouldAlert = true;
} else if (nodeName.includes('Database')) {
  severity = 'HIGH';
  shouldAlert = true;
  shouldRetry = true;
}

// Log error to database
// (Supabase insert to error_log table)

// Send alert if needed
if (shouldAlert) {
  // Discord webhook notification
}

return [{
  json: {
    error: error.message,
    severity: severity,
    should_retry: shouldRetry,
    timestamp: new Date().toISOString()
  }
}];
```

### Monitoring Dashboards

#### Key Metrics to Track

**Operational Health:**
- Scraping success rate (% of websites scraped successfully)
- Article extraction success rate
- Content generation success rate
- Posting success rate per platform
- Average workflow execution time

**Queue Health:**
- Current queue size
- Average time article spends in queue
- Articles deleted due to age (stale rate)

**Content Performance:**
- Posts per day (by platform)
- Average engagement rate (by platform, content type)
- Model win rates (first judge, second judge)
- Model performance (engagement per model)

**Cost Tracking:**
- Daily API costs (by provider)
- Cost per post
- Cost per engagement (CPE)

#### Implementation

**Option 1: Supabase + Custom Dashboard**
- Query metrics from database
- Build simple dashboard with Retool, Streamlit, or similar

**Option 2: Grafana + PostgreSQL**
- Connect Grafana to Supabase database
- Create dashboards with real-time metrics

**Sample Query (Daily Summary):**
```sql
SELECT 
  DATE(created_at) as date,
  COUNT(*) as total_articles,
  COUNT(*) FILTER (WHERE processed = true) as processed_articles,
  AVG(judge_score) as avg_score,
  COUNT(*) FILTER (WHERE judge_score >= 8) as high_quality_count
FROM articles
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### Notification Configuration

#### Discord Webhook Setup

Create channels:
- `#system-alerts` - Critical errors, authentication issues
- `#queue-status` - Queue size warnings
- `#manual-tasks` - TikTok videos ready, manual reviews needed

Example alert message format:
```javascript
{
  "content": null,
  "embeds": [{
    "title": "🚨 Queue Alert",
    "description": "Queue size has exceeded threshold",
    "color": 15258703, // Red for alerts
    "fields": [
      {
        "name": "Queue Size",
        "value": "67 articles",
        "inline": true
      },
      {
        "name": "Threshold",
        "value": "60",
        "inline": true
      },
      {
        "name": "Action",
        "value": "Judge strictness increased to score >= 7"
      }
    ],
    "timestamp": new Date().toISOString()
  }]
}
```

### Testing & Validation

#### Pre-Launch Checklist

**Infrastructure:**
- [ ] Supabase database created and tables set up
- [ ] All API keys obtained and stored securely
- [ ] n8n instance running (cloud or self-hosted)
- [ ] All required npm packages installed (canvas, ffmpeg)
- [ ] Social media business accounts created
- [ ] Discord monitoring channels created

**Workflow Testing:**
- [ ] Test scraping from all 5 websites
- [ ] Verify duplicate detection works
- [ ] Test extraction with sample HTML
- [ ] Validate first judge scoring makes sense
- [ ] Verify all 3 models generate content
- [ ] Check second judge picks reasonable winners
- [ ] Test image generation/acquisition
- [ ] Test video creation end-to-end
- [ ] Test podcast generation
- [ ] Verify posting to Instagram works
- [ ] Verify posting to Facebook works
- [ ] Verify posting to YouTube works
- [ ] Test TikTok export to folder
- [ ] Validate performance tracking fetches metrics

**Data Quality:**
- [ ] Manual review of 10 generated headlines
- [ ] Manual review of 5 carousel posts
- [ ] Manual review of 3 video scripts
- [ ] Manual review of 1 podcast episode
- [ ] Verify Slovak language quality
- [ ] Check for cultural appropriateness

**Cost Validation:**
- [ ] Run 24-hour test cycle
- [ ] Calculate actual API costs
- [ ] Verify costs match estimates
- [ ] Adjust if needed

---

## Cost Estimates

### Daily Operating Costs (Aggressive - 30 posts/day)

#### AI/ML Costs

**Extraction (GPT-5 Nano):**
- 120 articles/day × 75k input tokens = 9M tokens
- 120 articles × 1k output tokens = 120k tokens
- Cost: (9M × $0.15/1M) + (120k × $1.50/1M) = $1.53/day

**First Judge (GPT-5):**
- 120 articles × 500 input tokens (summary) = 60k tokens
- With prompt caching (90% discount): 6k tokens billed
- 120 articles × 500 output tokens = 60k tokens
- Cost: (6k × $1.25/1M) + (60k × $10/1M) = $0.61/day

**Content Generation (3 models):**
- 30 high-scoring articles
- Each model: 30 × 600 input + 30 × 1500 output tokens
- GPT-5 Mini: (18k × $0.50/1M) + (45k × $5/1M) = $0.24
- Haiku 4.5: (18k × $1/1M) + (45k × $5/1M) = $0.24
- Gemini 2.5 Flash: ~$0.20 (estimated)
- Total: $0.68/day

**Second Judge (GPT-5):**
- 30 articles × 3 versions × 400 tokens input = 36k tokens
- 30 articles × 200 tokens output = 6k tokens
- Cost: (36k × $1.25/1M) + (6k × $10/1M) = $0.11/day

**Image Generation (DALL-E 3):**
- ~10 images/day (when article images unavailable)
- 10 × $0.04 = $0.40/day

**Voice Synthesis (ElevenLabs):**
- Videos: 8 videos × 100 characters = 800 chars
- Podcasts: 2 episodes × 2000 characters = 4000 chars
- Total: 4800 chars/day = ~144k chars/month
- Cost: $22/month plan sufficient = $0.73/day

**Total AI/ML: ~$4.30/day = $129/month**

#### Infrastructure Costs

**Supabase:**
- Free tier sufficient for MVP (500MB database, 2GB bandwidth)
- Cost: $0/month initially

**n8n:**
- Self-hosted (recommended): $10-20/month VPS
- n8n Cloud: $50/month (Starter plan)
- Cost: $0.33-1.67/day

**Storage (images/videos):**
- Google Drive or similar: $1.99/month for 100GB
- Cost: $0.07/day

**Total Infrastructure: ~$0.40-1.74/day**

### Total Estimated Costs

**Conservative (10-15 posts/day):**
- AI/ML: ~$2.00/day = $60/month
- Infrastructure: ~$0.50/day = $15/month
- **Total: $75/month**

**Aggressive (25-35 posts/day):**
- AI/ML: ~$4.50/day = $135/month
- Infrastructure: ~$1.00/day = $30/month
- **Total: $165/month**

**Note:** Costs will decrease significantly once:
1. Model performance data identifies best models (can reduce from 3 to 1-2)
2. Prompt caching fully utilized (90% savings on repeated prompts)
3. Queue optimization reduces unnecessary generation

---

## Implementation Notes

### Development Phases

**Phase 1: Core Pipeline (Week 1-2)**
- Set up infrastructure (Supabase, n8n)
- Implement scraping + storage
- Build extraction module
- Test first judge
- **Milestone:** Can scrape and score articles

**Phase 2: Content Generation (Week 3-4)**
- Implement all 3 generator models
- Build second judge
- Test output quality
- **Milestone:** Can generate all content formats

**Phase 3: Media Creation (Week 5-6)**
- Image acquisition/generation
- Text overlay on images
- Video creation pipeline
- Podcast audio generation
- **Milestone:** Can create all media types

**Phase 4: Publishing (Week 7-8)**
- Instagram integration
- Facebook integration
- YouTube integration
- TikTok manual export
- Rate limiting
- **Milestone:** Can post to all platforms

**Phase 5: Tracking & Optimization (Week 9-10)**
- Performance tracking implementation
- Feedback loop to judges
- Model performance analytics
- Dashboard creation
- **Milestone:** System self-optimizes

**Phase 6: Testing & Launch (Week 11-12)**
- End-to-end testing
- Cost validation
- Content quality review
- Soft launch (limited posting)
- **Milestone:** Production ready

### Best Practices for n8n Workflows

#### 1. Modular Design
- Break complex workflows into smaller sub-workflows
- Use "Execute Workflow" node to call sub-workflows
- Each module should have clear input/output contracts

#### 2. Error Handling
- Always add Error Trigger nodes
- Implement retry logic with exponential backoff
- Log all errors to database for analysis

#### 3. Performance Optimization
- Use SplitInBatches for parallel processing
- Enable prompt caching where applicable
- Process large datasets in chunks (batch size: 10-20)

#### 4. Testing
- Use n8n's "Execute Node" feature to test individual nodes
- Create test workflows with sample data
- Validate all edge cases (empty responses, missing fields, etc.)

#### 5. Documentation
- Add Sticky Notes to workflows explaining logic
- Use descriptive node names ("Extract Article Summary" vs "Function1")
- Maintain a separate document with API credentials and configuration

#### 6. Version Control
- Export workflows as JSON regularly
- Store in Git repository
- Tag versions before major changes

#### 7. Monitoring
- Set up workflow execution logs
- Monitor execution times (identify bottlenecks)
- Track success/failure rates per node

### Security Considerations

#### 1. API Key Management
- Never hardcode API keys in workflows
- Use n8n's credential management system
- Rotate keys regularly (every 90 days)
- Use different keys for dev/production

#### 2. Data Privacy
- Slovak GDPR compliance required
- Don't store personal data from articles
- Implement data retention policy (delete old articles)
- Encrypt sensitive data in database

#### 3. Rate Limiting
- Respect platform API limits
- Implement circuit breakers (stop if too many failures)
- Add delays between requests to same endpoint

#### 4. Access Control
- Use separate n8n accounts for team members
- Implement role-based access (if using n8n Cloud)
- Audit workflow changes

### Troubleshooting Common Issues

#### Issue: Scraping fails
**Causes:** Website structure changed, anti-bot measures, SSL certificate errors
**Solutions:** 
- Update CSS selectors
- Add User-Agent headers
- Use RSS feeds instead
- Implement rotating proxies if needed

#### Issue: LLM responses invalid JSON
**Causes:** Temperature too high, unclear prompts, token limits
**Solutions:**
- Lower temperature (0.1-0.3)
- Add explicit JSON schema to prompts
- Increase max_tokens limit
- Add JSON validation node

#### Issue: Videos fail to create
**Causes:** FFmpeg not installed, missing codecs, file path issues
**Solutions:**
- Install FFmpeg: `apt-get install ffmpeg`
- Check temp file permissions
- Validate input file formats
- Add detailed error logging

#### Issue: Social media posting fails
**Causes:** Expired tokens, rate limits, content policy violations
**Solutions:**
- Refresh access tokens (FB tokens expire)
- Implement proper rate limiting
- Add content moderation before posting
- Review platform guidelines

#### Issue: Queue grows too large
**Causes:** Not enough posts being approved, generation too slow
**Solutions:**
- Lower judge score thresholds temporarily
- Increase posting frequency
- Optimize slow nodes (parallel processing)
- Add more posting windows

### Future Enhancements

**Short-term (3-6 months):**
- A/B testing different content formats
- Sentiment analysis on articles
- Automated topic clustering
- Multi-language support (Slovak + Czech)
- TikTok API integration (when approved)

**Medium-term (6-12 months):**
- Multiple content verticals (politics, sports, tech)
- Influencer partnership automation
- User engagement analysis (comment sentiment)
- Predictive virality scoring
- Automated thumbnail generation

**Long-term (12+ months):**
- Video editing AI (not just slideshows)
- Real-time trending topic detection
- Multi-account management
- White-label platform for other markets
- Advanced analytics dashboard

---

## Appendix

### Useful Resources

**n8n Documentation:**
- Official docs: https://docs.n8n.io/
- AI workflows: https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.ai-agent/
- Community templates: https://n8n.io/workflows/

**AI Model Documentation:**
- OpenAI API: https://platform.openai.com/docs/
- Anthropic Claude: https://docs.anthropic.com/
- Google Gemini: https://ai.google.dev/docs

**Social Media APIs:**
- Instagram Graph API: https://developers.facebook.com/docs/instagram-api/
- Facebook Graph API: https://developers.facebook.com/docs/graph-api/
- YouTube Data API: https://developers.google.com/youtube/v3
- TikTok for Developers: https://developers.tiktok.com/

**Voice & Media:**
- ElevenLabs API: https://elevenlabs.io/docs/
- FFmpeg documentation: https://ffmpeg.org/documentation.html

### Sample Prompts

**First Judge System Prompt:**
```
You are an expert Slovak celebrity gossip content evaluator. Rate articles 1-10 based on:
- Virality potential (controversy, emotion, celebrity prominence)
- Timeliness (breaking vs. old news)
- Visual potential (can this make compelling images/videos?)
- Slovak audience relevance

Current trending topics (prioritize): {trending_topics}
Queue status: {queue_size} articles waiting

Strictness level: {strictness_message}

Return JSON only:
{
  "score": 1-10,
  "reasoning": "...",
  "topic": "category",
  "format_assignment": {"podcast": bool, "video": bool, "carousel": bool, "headline": bool}
}
```

**Content Generator Prompt:**
```
Generate engaging Slovak celebrity gossip content in these formats:

HEADLINE: 140 char max, include emoji, scroll-stopping
CAROUSEL: 3-8 slides, 140 char each, storytelling flow
VIDEO: Conversational script, 10-120 sec, suggest music mood
PODCAST: 2-person dialogue (Male/Female), 45-90 sec, natural Slovak

Article: {article_summary}

Return JSON only with all formats.
```

**Second Judge Prompt:**
```
Compare these 3 versions and select the BEST for each format.

Criteria: engagement, clarity, Slovak language quality, virality potential

Versions: {all_versions}

Return JSON: {"headline_winner": "model", "carousel_winner": "model", ...}
```

### Contact & Support

For questions about this specification:
- n8n Community: https://community.n8n.io/
- AI/ML issues: Check provider documentation
- Slovak language quality: Consider hiring native speaker for review

---

**End of Technical Specification**

*Version 1.0 - October 16, 2025*

