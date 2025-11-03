# Slovak Celebrity Gossip - Task List

## Legend
- [ ] Not Started
- [→] In Progress
- [✓] Completed
- [✗] Blocked (waiting on dependencies)

---

## 📊 Progress Summary

### Completed
- ✅ **Phase 0: Initial Setup** - 100% Complete
- ✅ **Test Workflow** - Validated & Working
- ✅ **Infrastructure** - n8n + Supabase + API ready

### In Progress
- 🚀 **Phase 1: Data Collection Pipeline** - Ready to start!

### Timeline
- **Started**: 2025-11-03
- **Phase 0 Completed**: 2025-11-03
- **Current Status**: Ready to build production workflows

---

## Phase 0: Initial Setup ✅ **COMPLETED**

### Supabase Database Setup ✅
- [✓] Create Supabase account at https://supabase.com
- [✓] Create new project (Europe region)
- [✓] Copy project URL: `https://ftlwysaeliivaukqozbs.supabase.co`
- [✓] Copy anon/public key from Settings → API
- [✓] Run database schema SQL for `articles` table
- [✓] Run database schema SQL for `posts` table
- [✓] Run database schema SQL for `performance_metrics` table
- [✓] Run database schema SQL for `model_performance` table
- [✓] Verify all 4 tables exist in Supabase dashboard
- [✓] Test connection from n8n (created "Supabase account" credential)

### API Keys Collection ✅
**Phase 1 Keys** (Immediate Need):
- [✓] Get OpenAI API key from https://platform.openai.com/api-keys
- [✓] Add `SUPABASE_URL` to .env.local
- [✓] Add `SUPABASE_KEY` to .env.local (anon/public key)
- [✓] Add `OPENAI_API_KEY` to .env.local
- [✓] Verify .env.local has all Phase 1 keys

**Phase 2 Keys** (Week 2):
- [ ] Get Anthropic API key for Claude
- [ ] Get Google AI API key for Gemini
- [ ] Add `ANTHROPIC_API_KEY` to .env.local
- [ ] Add `GOOGLE_AI_API_KEY` to .env.local

**Phase 3 Keys** (Week 4):
- [ ] Get ElevenLabs API key for TTS
- [ ] Add `ELEVENLABS_API_KEY` to .env.local

**Phase 4 Keys** (Week 6):
- [ ] Get Facebook Page Access Token
- [ ] Get Instagram Account ID
- [ ] Set up YouTube OAuth (Client ID + Secret)
- [ ] Add `FB_PAGE_ACCESS_TOKEN` to .env.local
- [ ] Add `INSTAGRAM_ACCOUNT_ID` to .env.local
- [ ] Add `YOUTUBE_CLIENT_ID` to .env.local
- [ ] Add `YOUTUBE_CLIENT_SECRET` to .env.local

### n8n MCP Configuration ✅
- [✓] Verify n8n instance running at http://localhost:5678
- [✓] Test n8n-mcp connection with `mcp__n8n-mcp__get_database_statistics`
- [✓] Confirm n8n-skills are loaded in ~/.claude/skills/
- [✓] Create n8n credentials for Supabase (credential ID: woAUTvWByiJ9u8p2)
- [✓] Create n8n credentials for OpenAI

### Test Workflow - Connection Validation ✅
- [✓] Create test-supabase-connection.json workflow
- [✓] Fix critical expression syntax error (`{{ }}` → `` =`${}` ``)
- [✓] Add error handling (`continueOnFail: true` to all nodes)
- [✓] Deploy workflow to n8n instance (ID: FkBvvxdjYrMMqAKh)
- [✓] Configure field mappings in Supabase Insert node
- [✓] Test execution: Insert → Query → Cleanup
- [✓] Verify all 3 nodes execute successfully
- [✓] Confirm Supabase connection working
- [✓] Confirm n8n API deployment working

### Documentation Created ✅
- [✓] implementation-plan.md (40KB - complete 12-week roadmap)
- [✓] todo.md (this file - 300+ granular tasks)
- [✓] supabase-schema.sql (12KB - database schema + helpers)
- [✓] SETUP-GUIDE.md (15KB - Supabase connection guide)
- [✓] test-supabase-connection.json (test workflow)

---

## Phase 1: Data Collection Pipeline (Week 1)

### Sub-Workflow 1A: "Scraper - Hourly Data Collection"

#### Discovery & Configuration
- [ ] Search for Schedule Trigger node (`search_nodes`)
- [ ] Get essentials for Schedule Trigger node
- [ ] Search for HTTP Request node
- [ ] Get essentials for HTTP Request node with examples
- [ ] Search for Supabase node
- [ ] Get essentials for Supabase node with examples
- [ ] Search for IF node for error handling
- [ ] Get essentials for IF node

#### Build Schedule Trigger
- [ ] Configure Schedule Trigger node (cron: `0 * * * *`)
- [ ] Validate Schedule Trigger config (`validate_node_operation`)
- [ ] Fix any validation errors

#### Build HTTP Request Nodes (5 sources)
- [ ] Configure HTTP Request #1: topky.sk/celebrity
- [ ] Validate HTTP Request #1
- [ ] Configure HTTP Request #2: cas.sk/celebrity
- [ ] Validate HTTP Request #2
- [ ] Configure HTTP Request #3: pluska.sk/celebrity
- [ ] Validate HTTP Request #3
- [ ] Configure HTTP Request #4: refresher.sk/celebrity
- [ ] Validate HTTP Request #4
- [ ] Configure HTTP Request #5: startitup.sk/celebrity
- [ ] Validate HTTP Request #5

#### Build Error Handling
- [ ] Configure IF node per source (check HTTP status 200)
- [ ] Validate IF nodes
- [ ] Add error logging nodes (optional)

#### Build Storage
- [ ] Configure Supabase Insert node
- [ ] Set fields: source_url, source_website, raw_html, scraped_at
- [ ] Enable "Upsert" mode (ON CONFLICT DO NOTHING)
- [ ] Validate Supabase Insert config

#### Workflow Assembly
- [ ] Build complete workflow JSON with all nodes
- [ ] Add connections between nodes
- [ ] Validate complete workflow (`validate_workflow`)
- [ ] Fix connection errors if any
- [ ] Fix expression errors if any

#### Deployment & Testing
- [ ] Deploy workflow to n8n (`n8n_create_workflow`)
- [ ] Verify deployment (`n8n_validate_workflow`)
- [ ] Test with manual trigger (test 1-2 sources first)
- [ ] Check raw HTML stored in Supabase `articles` table
- [ ] Verify deduplication (try scraping same URL twice)
- [ ] Test error handling (disconnect internet for one source)
- [ ] Activate workflow in n8n UI (cannot be done via MCP)
- [ ] Wait 1 hour and verify automatic execution

#### Success Criteria
- [ ] Executes every hour automatically
- [ ] Stores HTML from at least 3/5 sources
- [ ] Continues on individual source failures
- [ ] No duplicate URLs stored (UNIQUE constraint works)

---

### Sub-Workflow 1B: "Extraction - HTML to Summary"

#### Discovery & Configuration
- [ ] Search for OpenAI node
- [ ] Get essentials for OpenAI node with examples
- [ ] Search for SplitInBatches node
- [ ] Get essentials for SplitInBatches node

#### Build Query & Batch Processing
- [ ] Configure Schedule Trigger (every 10 minutes: `*/10 * * * *`)
- [ ] Validate Schedule Trigger
- [ ] Configure Supabase Query node (SELECT * FROM articles WHERE processed = FALSE)
- [ ] Validate Supabase Query
- [ ] Configure SplitInBatches node (batch size: 10-20)
- [ ] Validate SplitInBatches

#### Build OpenAI Extraction
- [ ] Configure OpenAI node (model: gpt-5-nano or gpt-4o-mini)
- [ ] Write system prompt for extraction
- [ ] Set temperature: 0.1
- [ ] Set max tokens: 600
- [ ] Enable prompt caching (CRITICAL for cost savings)
- [ ] Set response format: JSON Object
- [ ] Validate OpenAI node config

#### Build Update Logic
- [ ] Configure Supabase Update node
- [ ] Set fields: summary, processed = TRUE
- [ ] Use WHERE clause: id = {{$json.id}}
- [ ] Validate Supabase Update

#### Workflow Assembly
- [ ] Build complete workflow JSON
- [ ] Add all node connections
- [ ] Validate workflow (`validate_workflow`)
- [ ] Fix any errors

#### Deployment & Testing
- [ ] Deploy workflow to n8n
- [ ] Verify deployment
- [ ] Insert 5-10 test articles into Supabase (with processed = FALSE)
- [ ] Trigger workflow manually
- [ ] Check summaries generated correctly
- [ ] Verify `processed = TRUE` after execution
- [ ] Check OpenAI dashboard for token usage (~500 tokens per article)
- [ ] Verify prompt caching is working (should see 90% savings on 2nd+ batch)
- [ ] Activate workflow in n8n UI

#### Cost Validation
- [ ] Calculate cost per article (target: ~$0.0001 with GPT-5 Nano)
- [ ] Verify prompt caching reduces cost by 90%
- [ ] Check batch processing is efficient

#### Success Criteria
- [ ] Processes unprocessed articles every 10 minutes
- [ ] Reduces 50k-100k tokens to ~500 tokens
- [ ] Prompt caching saves 90% on repeated system prompts
- [ ] Cost: ~$0.0001 per article or less
- [ ] Summary quality: readable Slovak, key info preserved

---

### Sub-Workflow 1C: "First Judge - Scoring & Format Assignment"

#### Discovery & Configuration
- [ ] Search for Code node
- [ ] Get essentials for Code node with examples
- [ ] Review IF node configuration (already done)

#### Build Queue Monitoring
- [ ] Configure Schedule Trigger (every 15 minutes: `*/15 * * * *`)
- [ ] Validate Schedule Trigger
- [ ] Configure Supabase Query #1 (get unscored articles: scored = FALSE)
- [ ] Validate Query #1
- [ ] Configure Supabase Query #2 (get queue size: COUNT(*) WHERE posted = FALSE)
- [ ] Validate Query #2

#### Build Dynamic Threshold Logic
- [ ] Configure Code node for threshold calculation
- [ ] Write JavaScript logic:
  ```javascript
  const queueSize = $json.queue_size;
  let minScore = 4;
  if (queueSize >= 60) minScore = 7;
  else if (queueSize >= 40) minScore = 6;
  else if (queueSize >= 20) minScore = 5;
  return [{json: {minScore}}];
  ```
- [ ] Validate Code node

#### Build OpenAI Judging
- [ ] Configure OpenAI node (model: gpt-5-mini or gpt-4o)
- [ ] Write system prompt for scoring (include format assignment rules)
- [ ] Set temperature: 0.3
- [ ] Enable prompt caching
- [ ] Set response format: JSON Object
- [ ] Validate OpenAI node

#### Build Conditional Logic
- [ ] Configure IF node (check if score >= minScore)
- [ ] Validate IF node with branch parameter
- [ ] Configure Supabase Update (TRUE branch): store judge_score, format_assignments, scored = TRUE
- [ ] Configure Supabase Update (FALSE branch): store judge_score = 0, scored = TRUE
- [ ] Validate both Update nodes

#### Workflow Assembly
- [ ] Build complete workflow JSON
- [ ] Add all node connections (including IF node branches with `branch` parameter)
- [ ] Validate workflow (`validate_workflow`)
- [ ] Fix any errors

#### Deployment & Testing
- [ ] Deploy workflow to n8n
- [ ] Verify deployment
- [ ] Test with queue size = 10 (minScore should be 4)
- [ ] Test with queue size = 25 (minScore should be 5)
- [ ] Test with queue size = 45 (minScore should be 6)
- [ ] Test with queue size = 65 (minScore should be 7)
- [ ] Verify format assignments match score ranges:
  - Score 8-10: ["podcast", "video", "carousel", "headline"]
  - Score 6-7: ["carousel", "headline"]
  - Score 4-5: ["headline"]
  - Score 1-3: []
- [ ] Check rejected articles marked correctly (scored = TRUE, judge_score = 0)
- [ ] Activate workflow in n8n UI

#### Success Criteria
- [ ] Dynamic threshold adjusts based on queue size
- [ ] Scores articles accurately (spot-check 10-20 articles)
- [ ] Format assignments follow spec rules
- [ ] Rejected articles marked correctly (don't reprocess)
- [ ] Cost: ~$0.0005 per article

---

## Phase 2: Content Generation (Week 2-3)

### Sub-Workflow 2: "Content Generator - Multi-Model Generation"

#### Discovery & Configuration
- [ ] Search for Anthropic node (Claude)
- [ ] Get essentials for Anthropic node with examples
- [ ] Search for Google Gemini node
- [ ] Get essentials for Google Gemini node with examples
- [ ] Review OpenAI node (already configured)

#### Build Query & Batching
- [ ] Configure Schedule Trigger (every 20 minutes)
- [ ] Configure Supabase Query (get scored articles with format_assignments != '[]' and no posts yet)
- [ ] Configure SplitInBatches (batch size: 5-10)

#### Build Model 1: OpenAI (GPT-5 Mini)
- [ ] Configure OpenAI node for content generation
- [ ] Write system prompt (generate ALL formats in one call)
- [ ] Include format specifications (headline, carousel, video, podcast)
- [ ] Set temperature: 0.7 (creative task)
- [ ] Enable prompt caching
- [ ] Set response format: JSON Object
- [ ] Validate OpenAI node

#### Build Model 2: Anthropic (Claude Haiku 4.5)
- [ ] Configure Anthropic node
- [ ] Use same system prompt as OpenAI
- [ ] Set temperature: 0.7
- [ ] Enable prompt caching
- [ ] Validate Anthropic node

#### Build Model 3: Google Gemini (2.5 Flash)
- [ ] Configure Google Gemini node
- [ ] Use same system prompt
- [ ] Set temperature: 0.7
- [ ] Enable prompt caching (if supported)
- [ ] Validate Gemini node

#### Build Storage Logic
- [ ] Configure Supabase Insert for Model 1 output
- [ ] Configure Supabase Insert for Model 2 output
- [ ] Configure Supabase Insert for Model 3 output
- [ ] Set fields: article_id, platform, content_type, generating_model, content (JSONB)
- [ ] Validate all Insert nodes

#### Workflow Assembly
- [ ] Build workflow with 3 parallel branches (one per model)
- [ ] Add all node connections
- [ ] Validate workflow (`validate_workflow`)
- [ ] Fix any errors

#### Deployment & Testing
- [ ] Deploy workflow to n8n
- [ ] Verify deployment
- [ ] Test with 5-10 sample articles
- [ ] Verify all 3 models generate content in parallel
- [ ] Check each model generates ALL formats in ONE call (not 4 separate calls)
- [ ] Verify Slovak language quality (natural, with slang)
- [ ] Measure token usage per model
- [ ] Compare model outputs for quality
- [ ] Verify content stored correctly in `posts` table
- [ ] Activate workflow in n8n UI

#### Cost Validation
- [ ] Calculate cost per article (all 3 models combined)
- [ ] Target: ~$0.01-0.03 per article
- [ ] Verify prompt caching is working (90% savings)

#### Success Criteria
- [ ] All 3 models generate content in parallel
- [ ] Each model generates ALL formats in ONE API call (4x token savings)
- [ ] Prompt caching enabled (90% savings on repeated prompts)
- [ ] Content stored correctly in `posts` table
- [ ] Cost: ~$0.01-0.03 per article (all 3 models combined)

---

### Sub-Workflow 3: "Second Judge - Best Version Selection"

#### Build Query & Batching
- [ ] Configure Schedule Trigger (every 30 minutes)
- [ ] Configure Supabase Query (get articles with 3 generated posts but no selected post)
- [ ] Configure SplitInBatches (batch size: 10)

#### Build Comparison Logic per Format
- [ ] Configure Code node to group 3 versions by format (headline, carousel, video, podcast)
- [ ] For each format, configure OpenAI node (GPT-5) to compare and judge
- [ ] Write system prompt for comparison
- [ ] Set temperature: 0.3
- [ ] Set response format: JSON Object with winner, score, reasoning
- [ ] Validate OpenAI comparison node

#### Build Selection & Tracking
- [ ] Configure Supabase Update (mark winner as selected = TRUE, store judge_score)
- [ ] Configure Supabase Upsert for `model_performance` table (increment judge_wins for winner)
- [ ] Validate Update and Upsert nodes

#### Workflow Assembly
- [ ] Build complete workflow JSON
- [ ] Add all node connections
- [ ] Validate workflow
- [ ] Fix any errors

#### Deployment & Testing
- [ ] Deploy workflow to n8n
- [ ] Verify deployment
- [ ] Test with 5-10 articles with all 3 versions
- [ ] Verify selection logic (winner marked correctly)
- [ ] Check `model_performance` table updates
- [ ] Spot-check judge decisions (are they reasonable?)
- [ ] Activate workflow in n8n UI

#### Success Criteria
- [ ] Selects best version per format
- [ ] Updates `model_performance` tracking
- [ ] Stores judge reasoning for debugging
- [ ] Cost: ~$0.005 per article

---

## Phase 3: Media Creation (Week 4-5)

### Sub-Workflow 4A: "Media Creator - Images"

#### Discovery & Configuration
- [ ] Search for DALL-E node
- [ ] Get essentials for DALL-E node with examples
- [ ] Review Code node (already configured)

#### Build Query & Image Extraction
- [ ] Configure Schedule Trigger (every 30 minutes)
- [ ] Configure Supabase Query (get selected posts needing images)
- [ ] Configure Code node to extract images from HTML (regex)
- [ ] Configure IF node (check if image extracted)
- [ ] Validate nodes

#### Build DALL-E Fallback
- [ ] Configure DALL-E node (FALSE branch - no image found)
- [ ] Set prompt: "Modern, bold, news-worthy image for: {summary}"
- [ ] Set size: 1024x1024
- [ ] Validate DALL-E node

#### Build Image Overlay
- [ ] Configure Code node for canvas text overlay
- [ ] Install Node.js canvas library in n8n
- [ ] Write JavaScript for semi-transparent overlay + text
- [ ] Validate Code node

#### Build Upload & Storage
- [ ] Configure HTTP Request node for image upload (Supabase Storage or Cloudinary)
- [ ] Configure Supabase Update (store media_urls array)
- [ ] Validate nodes

#### Workflow Assembly & Testing
- [ ] Build complete workflow JSON
- [ ] Validate workflow
- [ ] Deploy to n8n
- [ ] Test with 10 sample articles
- [ ] Test extraction (articles with images)
- [ ] Test DALL-E generation (articles without images)
- [ ] Verify canvas overlay renders correctly
- [ ] Check uploaded images are accessible
- [ ] Activate workflow

#### Success Criteria
- [ ] Extracts images when available (saves DALL-E costs)
- [ ] Generates images when needed
- [ ] Text overlay readable and attractive
- [ ] Images stored and URLs saved

---

### Sub-Workflow 4B: "Media Creator - Videos"

#### Discovery & Configuration
- [ ] Search for ElevenLabs node
- [ ] Get essentials for ElevenLabs node
- [ ] Search for Whisper node (OpenAI)
- [ ] Get essentials for Whisper node

#### Build Query
- [ ] Configure Schedule Trigger (every 30 minutes)
- [ ] Configure Supabase Query (get selected posts with content_type = 'video' needing media)

#### Build Voiceover
- [ ] Configure ElevenLabs node for voiceover
- [ ] Select Multilingual v2 model (Slovak support)
- [ ] Map script from content.script
- [ ] Validate ElevenLabs node

#### Build Captions
- [ ] Configure Whisper node (OpenAI)
- [ ] Set language: Slovak
- [ ] Set format: SRT
- [ ] Validate Whisper node

#### Build Music Selection
- [ ] Configure Code node to select background music
- [ ] Map moods to music files
- [ ] Validate Code node

#### Build Video Assembly
- [ ] Configure Code node for FFmpeg assembly
- [ ] Write FFmpeg command: slideshow + voiceover + music (30% volume) + captions
- [ ] Test FFmpeg command separately
- [ ] Validate Code node

#### Build Upload & Storage
- [ ] Configure HTTP Request for video upload
- [ ] Configure Supabase Update (store video URL)
- [ ] Validate nodes

#### Workflow Assembly & Testing
- [ ] Build complete workflow JSON
- [ ] Validate workflow
- [ ] Deploy to n8n
- [ ] Test voiceover quality (natural Slovak)
- [ ] Test caption accuracy
- [ ] Test FFmpeg assembly (manual verification)
- [ ] Check video plays correctly on mobile
- [ ] Activate workflow

#### Success Criteria
- [ ] Voiceover sounds natural (Slovak accent)
- [ ] Captions accurate and synced
- [ ] Background music at 30% volume
- [ ] Video format works on TikTok/Instagram

---

### Sub-Workflow 4C: "Media Creator - Podcasts"

#### Build Query & Batching
- [ ] Configure Schedule Trigger (every 6 hours)
- [ ] Configure Supabase Query (get 5 posts with content_type = 'podcast' and judge_score >= 8)

#### Build Episode Structure
- [ ] Configure OpenAI node for episode structure generation
- [ ] Write system prompt (intro, 5 segments, transitions, outro)
- [ ] Validate OpenAI node

#### Build Audio Generation
- [ ] Configure ElevenLabs node for male host voice
- [ ] Configure ElevenLabs node for female host voice
- [ ] Validate both nodes

#### Build Audio Concatenation
- [ ] Configure Code node for FFmpeg concatenation
- [ ] Write FFmpeg command: intro + segment1 + transition1 + ... + outro
- [ ] Validate Code node

#### Build YouTube Video Creation
- [ ] Configure Code node for YouTube video (audio + visualizer)
- [ ] Write FFmpeg command: waveform visualizer + slideshow
- [ ] Validate Code node

#### Build Upload & Storage
- [ ] Configure HTTP Request for audio upload
- [ ] Configure HTTP Request for video upload
- [ ] Configure Supabase Update (store podcast/video URLs)
- [ ] Validate nodes

#### Workflow Assembly & Testing
- [ ] Build complete workflow JSON
- [ ] Validate workflow
- [ ] Deploy to n8n
- [ ] Test 5-article batch processing
- [ ] Verify dialogue sounds natural (male/female alternation)
- [ ] Check transitions are smooth
- [ ] Test YouTube video rendering
- [ ] Activate workflow

#### Success Criteria
- [ ] Batches 5 articles per episode
- [ ] Dialogue flows naturally
- [ ] Total duration 5-10 minutes
- [ ] YouTube video looks professional

---

## Phase 4: Publishing (Week 6-7)

### Sub-Workflow 5: "Publisher - Multi-Platform Posting"

#### Discovery & Configuration
- [ ] Search for Instagram node (or HTTP Request for Graph API)
- [ ] Get essentials for Instagram posting
- [ ] Search for Facebook node
- [ ] Get essentials for Facebook posting
- [ ] Search for YouTube node
- [ ] Get essentials for YouTube posting

#### Build Query & Rate Limiting
- [ ] Configure Schedule Trigger (6 times per day: 7am, 10am, 1pm, 4pm, 7pm, 10pm)
- [ ] Configure Supabase Query (get queue of selected posts, posted = FALSE)
- [ ] Configure Supabase Query (get recent posts from last 24 hours)
- [ ] Configure Code node for rate limit check
- [ ] Write JavaScript logic:
  - Instagram/Facebook: Max 1 per window (3 hours apart)
  - YouTube: Max 2-3 per day
  - TikTok: Manual (alert user)
- [ ] Configure IF node (check if can post)
- [ ] Validate nodes

#### Build Platform Posting - Instagram
- [ ] Configure HTTP Request to Instagram Graph API
- [ ] Map fields: image_url, caption
- [ ] Handle API errors (rate limits, auth failures)
- [ ] Validate Instagram posting

#### Build Platform Posting - Facebook
- [ ] Configure HTTP Request to Facebook Graph API
- [ ] Map fields: message, link, image
- [ ] Handle API errors
- [ ] Validate Facebook posting

#### Build Platform Posting - YouTube
- [ ] Configure HTTP Request to YouTube Data API
- [ ] Map fields: title, description, video_file
- [ ] Handle OAuth flow
- [ ] Handle API errors
- [ ] Validate YouTube posting

#### Build Platform Posting - TikTok
- [ ] Configure manual upload tracking (no API in MVP)
- [ ] Configure Discord webhook to alert user
- [ ] Provide download link for video

#### Build Post Tracking
- [ ] Configure Supabase Update (mark posted = TRUE, store posted_at, post_url)
- [ ] Configure Discord webhook (optional) to notify team
- [ ] Validate nodes

#### Workflow Assembly & Testing
- [ ] Build complete workflow JSON with Switch node for platforms
- [ ] Validate workflow
- [ ] Deploy to n8n
- [ ] Test with test accounts (Instagram test account, etc.)
- [ ] Verify rate limiting logic (don't post twice in 3 hours)
- [ ] Test each platform API separately
- [ ] Monitor for API errors
- [ ] Activate workflow

#### Success Criteria
- [ ] Posts to Instagram/Facebook 6 times per day max
- [ ] Posts to YouTube 2-3 times per day
- [ ] Respects 3-hour spacing between posts
- [ ] Handles API errors gracefully (retry with backoff)

---

## Phase 5: Performance Tracking (Week 8-9)

### Sub-Workflow 6: "Performance Tracker - Engagement Metrics"

#### Build Query & Checkpoint Logic
- [ ] Configure Schedule Trigger (every hour)
- [ ] Configure Supabase Query (get posts at 1hr checkpoint: posted_at 60-70 mins ago)
- [ ] Configure Supabase Query (get posts at 6hr checkpoint: posted_at 6-7 hours ago)
- [ ] Configure Supabase Query (get posts at 24hr checkpoint: posted_at 24-25 hours ago)
- [ ] Configure Switch node to route by checkpoint

#### Build Platform Metrics - Instagram
- [ ] Configure HTTP Request to Instagram Graph API
- [ ] Fetch: likes, comments, saves, views
- [ ] Handle API errors
- [ ] Validate Instagram metrics

#### Build Platform Metrics - Facebook
- [ ] Configure HTTP Request to Facebook Graph API
- [ ] Fetch: likes, comments, shares
- [ ] Handle API errors
- [ ] Validate Facebook metrics

#### Build Platform Metrics - YouTube
- [ ] Configure HTTP Request to YouTube Data API
- [ ] Fetch: views, likes, comments
- [ ] Handle API errors
- [ ] Validate YouTube metrics

#### Build Platform Metrics - TikTok
- [ ] Configure manual entry workflow (for MVP)
- [ ] Alert user to enter metrics manually
- [ ] Provide web form or Discord bot

#### Build Engagement Rate Calculation
- [ ] Configure Code node to calculate engagement rate
- [ ] Formula: (likes + comments*2 + shares*3) / views * 100
- [ ] Validate Code node

#### Build Storage & Model Performance Update
- [ ] Configure Supabase Insert (store in performance_metrics table)
- [ ] Configure Supabase Update (update model_performance rolling average)
- [ ] Validate nodes

#### Workflow Assembly & Testing
- [ ] Build complete workflow JSON
- [ ] Validate workflow
- [ ] Deploy to n8n
- [ ] Test checkpoint timing (posts collected at right times)
- [ ] Verify engagement rate calculation
- [ ] Check model_performance updates correctly
- [ ] Test feedback loop (spot-check judge decisions change)
- [ ] Activate workflow

#### Success Criteria
- [ ] Collects metrics at 1hr, 6hr, 24hr checkpoints
- [ ] Engagement rate calculated correctly
- [ ] Model performance tracked over time
- [ ] Data feeds back to improve future judging

---

## Phase 6: Testing & Launch (Week 10-12)

### Integration Testing
- [ ] Test complete pipeline end-to-end with 5 articles
- [ ] Test complete pipeline with 10 articles
- [ ] Test complete pipeline with 20 articles
- [ ] Monitor execution logs for errors
- [ ] Verify data flows correctly between sub-workflows
- [ ] Check error handling:
  - Disconnect internet during scraping
  - Invalid API key
  - Database connection failure
  - Rate limit exceeded
  - Content policy violation
- [ ] Test all 9 sub-workflows together

### Cost Validation
- [ ] Track token usage for 24-hour period
- [ ] Calculate daily cost breakdown:
  - Extraction (GPT-5 Nano): $___
  - First Judge (GPT-5 Mini): $___
  - Content Generation (3 models): $___
  - Second Judge (GPT-5): $___
  - Image Generation (DALL-E): $___
  - Voiceover (ElevenLabs): $___
  - Captions (Whisper): $___
  - Total: $___ (target: ~$4.30/day)
- [ ] Verify prompt caching is working (90% savings)
- [ ] Check batch processing reduces API calls
- [ ] Identify cost optimization opportunities

### Performance Testing
- [ ] Measure execution time per sub-workflow:
  - Scraping: ___ minutes
  - Extraction: ___ minutes
  - First Judge: ___ minutes
  - Content Generation: ___ minutes
  - Second Judge: ___ minutes
  - Media Creation: ___ minutes
  - Publishing: ___ minutes
  - Performance Tracking: ___ minutes
- [ ] Test queue processing speed (can handle 30 posts/day?)
- [ ] Check rate limiting works correctly (6 posts/day)
- [ ] Monitor Supabase performance (query speed, connection pool)
- [ ] Test parallel processing (3 models generate simultaneously)

### Quality Assurance
- [ ] Review 20 generated headlines (scroll-stopping?)
- [ ] Review 10 generated carousels (storytelling flow?)
- [ ] Review 5 generated videos (natural Slovak?)
- [ ] Review 2 generated podcasts (engaging dialogue?)
- [ ] Check image overlay quality (readable?)
- [ ] Check video quality (mobile-friendly?)
- [ ] Check caption accuracy (Slovak transcription)
- [ ] Verify format assignments match quality (8-10 = all formats, etc.)

### Soft Launch
- [ ] Start with 1 article per day
- [ ] Post to test accounts only (Instagram test, etc.)
- [ ] Monitor engagement metrics for 1 week
- [ ] Collect user feedback
- [ ] Increase to 3 articles per day
- [ ] Monitor for 1 week
- [ ] Increase to 10 articles per day
- [ ] Monitor for 1 week
- [ ] Increase to 30 articles per day (target)

### Production Monitoring Setup
- [ ] Set up Discord alerts for critical errors:
  - All scrapers fail
  - Database connection lost
  - API authentication fails
  - Rate limit exceeded (unexpected)
  - Content policy violation
- [ ] Create cost monitoring dashboard
- [ ] Set up daily cost alerts (if > $5/day)
- [ ] Track model performance weekly
- [ ] Review engagement metrics weekly
- [ ] Adjust judge thresholds based on data

### Documentation
- [ ] Document scraper URL patterns (in case sites change)
- [ ] Document API rate limits per platform
- [ ] Document error handling procedures
- [ ] Document manual TikTok upload process
- [ ] Document how to add new scrapers
- [ ] Document how to swap AI models
- [ ] Create troubleshooting guide

### Launch Checklist
- [ ] All 9 sub-workflows deployed and activated
- [ ] All API keys valid and tested
- [ ] Supabase database optimized (indexes, etc.)
- [ ] Rate limiting tested and working
- [ ] Cost tracking in place
- [ ] Error monitoring in place
- [ ] Team trained on manual processes (TikTok upload)
- [ ] Backup plan for critical failures
- [ ] Ready for production traffic

---

## Ongoing Maintenance (Post-Launch)

### Daily Tasks
- [ ] Check Discord for error alerts
- [ ] Verify daily cost is within budget (~$4.30/day)
- [ ] Spot-check content quality (5 posts per day)
- [ ] Manual TikTok uploads (8-10 per day)

### Weekly Tasks
- [ ] Review model performance (which models win most?)
- [ ] Review engagement metrics (which formats perform best?)
- [ ] Adjust judge thresholds if needed
- [ ] Check for broken scrapers (website changes)
- [ ] Review token usage trends

### Monthly Tasks
- [ ] Analyze 30-day cost trends
- [ ] Review and optimize underperforming models
- [ ] Test new AI models (if available)
- [ ] Update format specifications based on engagement data
- [ ] Expand scraper sources (add new websites)
- [ ] Review and update content generation prompts

---

## 🎯 Status Summary

**Phase 0 (Setup)**: ✅ **100% Complete** (23/23 tasks)
- Supabase database configured with 4 tables
- All Phase 1 API keys configured
- n8n + n8n-mcp working
- Test workflow validated

**Phase 1 (Data Collection)**: ⏳ **0% Complete** (0/89 tasks)
- Ready to start building production workflows
- Next: Sub-Workflow 1A (Scraper)

**Overall Progress**: 23/389 tasks complete (6%)

---

*Last Updated: 2025-11-03 13:45 UTC*
*Total Tasks: 389 (23 completed, 366 remaining)*
*Current Phase: Phase 1 - Data Collection Pipeline*
