# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Slovak Celebrity Gossip Content Automation System** - an n8n-based workflow automation project that scrapes Slovak celebrity news, generates multi-format social media content using AI, and publishes to Instagram, Facebook, TikTok, and YouTube.

**Target Platform:** n8n workflow automation
**Content Language:** Slovak
**Architecture:** Modular pipeline with 9 main components

## System Architecture

The system follows a complete content automation pipeline:

```
Scraping (hourly) → Extraction → Storage (Supabase) →
First Judge (scoring & format assignment) → Content Generation (3 models) →
Second Judge (best version selection) → Media Creation → Publishing (rate-limited) →
Performance Tracking (feedback loop)
```

### Key Components

1. **Data Collection Module**: Hourly scraping of 5 Slovak celebrity news sites (topky.sk, cas.sk, pluska.sk, refresher.sk, startitup.sk)
2. **Storage & Deduplication**: Supabase PostgreSQL with 4 main tables (articles, posts, performance_metrics, model_performance)
3. **Extraction Module**: GPT-5 Nano condenses raw HTML (50k-100k tokens) to summaries (~500 tokens)
4. **First Judge Module**: GPT-5 scores articles 1-10, assigns content formats based on quality with dynamic strictness based on queue size
5. **Content Generation Module**: 3 models (GPT-5 Mini, Claude Haiku 4.5, Gemini 2.5 Flash) each generate all formats in one call
6. **Second Judge Module**: GPT-5 compares 3 versions and selects best for each format
7. **Media Creation Module**: Image acquisition/generation (DALL-E), text overlay (Node.js canvas), video creation (FFmpeg + ElevenLabs TTS + Whisper captions), podcast audio generation
8. **Publishing Module**: Posts to platforms with smart scheduling (6 posting windows: 7am, 10am, 1pm, 4pm, 7pm, 10pm) and rate limiting
9. **Performance Tracking Module**: Measures engagement at 1hr, 6hr, 24hr checkpoints; feeds data back to judges

### Content Formats & Scoring Rules

- **Score 8-10**: Podcast + Video + Carousel + Headline
- **Score 6-7**: Carousel + Headline only
- **Score 4-5**: Headline only
- **Score 1-3**: Skip (don't generate)

### Dynamic Queue-Based Judging

- Queue < 20: Accept scores 4+
- Queue 20-40: Accept scores 5+
- Queue 40-60: Accept scores 6+
- Queue 60+: Accept scores 7+ only

## Database Schema

### Tables

**articles**: Stores scraped articles with fields: id, source_url, source_website, title, content, summary, judge_score, format_assignments (JSONB), processed, scraped_at

**posts**: Stores generated content with fields: id, article_id, platform, content_type, generating_model, judge_score, content (JSONB), media_urls, posted_at, post_url

**performance_metrics**: Stores engagement data with fields: id, post_id, checkpoint (1hr/6hr/24hr), likes, comments, shares, views, engagement_rate

**model_performance**: Tracks AI model effectiveness with fields: id, model_name, content_type, judge_wins, avg_engagement, total_posts

## n8n Development Guidelines

### Workflow Structure

- Break complex workflows into sub-workflows using "Execute Workflow" node
- Use SplitInBatches nodes (batch size 10-20) for parallel processing
- Enable prompt caching on LLM nodes (saves 90% on repeated system prompts)
- Add Error Trigger nodes at workflow level for global error handling

### Common Node Patterns

**Scraping**: Schedule Trigger (cron: `0 * * * *`) → HTTP Request nodes per website → IF nodes for error handling

**Database Operations**: Use Supabase node for all CRUD operations
- **CRITICAL**: NEVER use `dataMode: "autoMapInputData"` in Supabase nodes - it fails to map fields correctly
- ALWAYS use `dataMode: "defineBelow"` with explicit field mappings using `fieldsUi.fieldValues`
- Example:
  ```json
  {
    "dataMode": "defineBelow",
    "fieldsUi": {
      "fieldValues": [
        {"fieldId": "column_name", "fieldValue": "={{ $json.field_name }}"}
      ]
    }
  }
  ```

**Upsert Pattern** (Supabase doesn't have native upsert, use pre-check pattern):
  ```
  Supabase Get (filter by unique key)
  → IF node (check if record exists)
    → TRUE branch: Supabase Update node
    → FALSE branch: Supabase Insert node
  ```
- This pattern avoids duplicate key constraint errors
- Check for existing record by unique column (e.g., source_url)
- IF node condition: `{{ $json.id !== undefined }}` or check array length
- Update branch: Updates existing record with new data
- Insert branch: Creates new record

**LLM Calls**: OpenAI/Anthropic/Google Gemini nodes with:
- System prompts for context
- Response Format: JSON Object
- Temperature: 0.1 (extraction), 0.3 (judging), 0.7 (generation)
- Enable caching where system prompt is static

**Media Processing**: Code nodes with Node.js for canvas (image overlay) and FFmpeg (video creation)

### Error Handling Strategy

- **Scraping failures**: Continue with remaining sources, log only if all fail
- **API rate limits**: Exponential backoff (1min, 2min, 4min), max 3 retries
- **Authentication errors**: Alert immediately, pause posting
- **Database connection loss**: Retry with backoff (5s, 10s, 20s, 40s, 80s), max 5 attempts
- **Content policy violations**: Mark failed, don't retry, alert for manual review

### Rate Limits

- **Instagram/Facebook**: 1 post per window (6/day max), 3 hours apart
- **YouTube**: 2-3 videos/day
- **TikTok**: Manual upload for MVP (8-10/day target when API available)

## Environment Variables

Required in .env.local (already present with N8N_APIKEY):

```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_AI_API_KEY=...
ELEVENLABS_API_KEY=...
SUPABASE_URL=...
SUPABASE_KEY=...
FB_PAGE_ACCESS_TOKEN=...
INSTAGRAM_ACCOUNT_ID=...
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
DISCORD_WEBHOOK_URL=...
```

## Cost Optimization

Current estimated costs (30 posts/day): **~$4.30/day for AI/ML, ~$165/month total**

**Key optimization strategies:**
1. Use GPT-5 Nano for simple extraction (cheapest)
2. Enable prompt caching (90% savings on repeated prompts)
3. Generate all formats in ONE API call per model (reduces input tokens 4x)
4. Process articles in parallel batches (10-20 at a time)
5. Queue-based strictness reduces low-quality generation
6. Model performance tracking allows dropping underperforming models

## Content Generation

### Format Specifications

**Headline**: Max 140 characters, include emoji if relevant, scroll-stopping impact

**Carousel**: 3-8 slides, max 140 chars each, storytelling flow (hook → details → CTA)

**Video**: 10-120 seconds, conversational script, includes background_music_mood suggestion (upbeat/dramatic/sad/chill/energetic)

**Podcast**: 2-person dialogue (Male/Female hosts), 45-90 seconds per story, 5 stories per episode, natural Slovak with slang

### Slovak Language Requirements

- Content must be in fluent, natural Slovak
- Use cultural references Slovak audience understands
- Employ Slovak slang and informal language appropriately
- Target audience: Slovak-speaking social media users interested in celebrity/gossip content

## Media Creation Pipeline

**Images**:
1. Try extracting from source article HTML (regex: `/<img[^>]+src="([^">]+)"/g`)
2. If none found, generate with DALL-E 3 (prompt includes story + "modern, bold, news-worthy")
3. Add text overlay using Node.js canvas library (semi-transparent bottom overlay + centered text)

**Videos** (TikTok/Reels format):
1. Generate voiceover with ElevenLabs TTS (multilingual v2 model)
2. Create captions with Whisper API (language: Slovak, format: SRT)
3. Select background music based on mood
4. Combine with FFmpeg: slideshow of images + voiceover + music (30% volume) + captions

**Podcasts**:
1. Batch 5 high-scoring articles (score >= 8)
2. Generate dialogue for each with intro/transitions/outro
3. Create audio segments per speaker (ElevenLabs with separate Male/Female voice IDs)
4. Concatenate segments with FFmpeg
5. Create YouTube video from podcast (slideshow + audio + visualizer)

## Development Workflow

### Phase Progression

1. **Core Pipeline** (Week 1-2): Scraping, storage, extraction, first judge
2. **Content Generation** (Week 3-4): 3 model generators, second judge
3. **Media Creation** (Week 5-6): Images, videos, podcasts
4. **Publishing** (Week 7-8): Platform integrations, rate limiting
5. **Tracking & Optimization** (Week 9-10): Performance metrics, feedback loop
6. **Testing & Launch** (Week 11-12): End-to-end testing, soft launch

### Testing Checklist Categories

Each component has a testing checklist in the spec document covering:
- Functional correctness (does it work?)
- Data quality (is output good?)
- Performance (speed, token usage)
- Error handling (graceful failures?)
- Cost validation (within budget?)

## n8n-MCP Development Guide

You are an expert in n8n automation software using n8n-MCP tools. Your role is to design, build, and validate n8n workflows with maximum accuracy and efficiency.

## Core Principles

### 1. Silent Execution
CRITICAL: Execute tools without commentary. Only respond AFTER all tools complete.

❌ BAD: "Let me search for Slack nodes... Great! Now let me get details..."
✅ GOOD: [Execute search_nodes and get_node_essentials in parallel, then respond]

### 2. Parallel Execution
When operations are independent, execute them in parallel for maximum performance.

✅ GOOD: Call search_nodes, list_nodes, and search_templates simultaneously
❌ BAD: Sequential tool calls (await each one before the next)

### 3. Templates First
ALWAYS check templates before building from scratch (2,709 available).

### 4. Multi-Level Validation
Use validate_node_minimal → validate_node_operation → validate_workflow pattern.

### 5. Never Trust Defaults
⚠️ CRITICAL: Default parameter values are the #1 source of runtime failures.
ALWAYS explicitly configure ALL parameters that control node behavior.

## Workflow Process

1. **Start**: Call `tools_documentation()` for best practices

2. **Template Discovery Phase** (FIRST - parallel when searching multiple)
   - `search_templates_by_metadata({complexity: "simple"})` - Smart filtering
   - `get_templates_for_task('webhook_processing')` - Curated by task
   - `search_templates('slack notification')` - Text search
   - `list_node_templates(['n8n-nodes-base.slack'])` - By node type

   **Filtering strategies**:
   - Beginners: `complexity: "simple"` + `maxSetupMinutes: 30`
   - By role: `targetAudience: "marketers"` | `"developers"` | `"analysts"`
   - By time: `maxSetupMinutes: 15` for quick wins
   - By service: `requiredService: "openai"` for compatibility

3. **Node Discovery** (if no suitable template - parallel execution)
   - Think deeply about requirements. Ask clarifying questions if unclear.
   - `search_nodes({query: 'keyword', includeExamples: true})` - Parallel for multiple nodes
   - `list_nodes({category: 'trigger'})` - Browse by category
   - `list_ai_tools()` - AI-capable nodes

4. **Configuration Phase** (parallel for multiple nodes)
   - `get_node_essentials(nodeType, {includeExamples: true})` - 10-20 key properties
   - `search_node_properties(nodeType, 'auth')` - Find specific properties
   - `get_node_documentation(nodeType)` - Human-readable docs
   - Show workflow architecture to user for approval before proceeding

5. **Validation Phase** (parallel for multiple nodes)
   - `validate_node_minimal(nodeType, config)` - Quick required fields check
   - `validate_node_operation(nodeType, config, 'runtime')` - Full validation with fixes
   - Fix ALL errors before proceeding

6. **Building Phase**
   - If using template: `get_template(templateId, {mode: "full"})`
   - **MANDATORY ATTRIBUTION**: "Based on template by **[author.name]** (@[username]). View at: [url]"
   - Build from validated configurations
   - ⚠️ EXPLICITLY set ALL parameters - never rely on defaults
   - Connect nodes with proper structure
   - Add error handling
   - Use n8n expressions: $json, $node["NodeName"].json
   - Build in artifact (unless deploying to n8n instance)

7. **Workflow Validation** (before deployment)
   - `validate_workflow(workflow)` - Complete validation
   - `validate_workflow_connections(workflow)` - Structure check
   - `validate_workflow_expressions(workflow)` - Expression validation
   - Fix ALL issues before deployment

8. **Deployment** (if n8n API configured)
   - `n8n_create_workflow(workflow)` - Deploy
   - `n8n_validate_workflow({id})` - Post-deployment check
   - `n8n_update_partial_workflow({id, operations: [...]})` - Batch updates
   - `n8n_trigger_webhook_workflow()` - Test webhooks

## Critical Warnings

### ⚠️ Never Trust Defaults
Default values cause runtime failures. Example:
```json
// ❌ FAILS at runtime
{resource: "message", operation: "post", text: "Hello"}

// ✅ WORKS - all parameters explicit
{resource: "message", operation: "post", select: "channel", channelId: "C123", text: "Hello"}
```

### ⚠️ Example Availability
`includeExamples: true` returns real configurations from workflow templates.
- Coverage varies by node popularity
- When no examples available, use `get_node_essentials` + `validate_node_minimal`

## Validation Strategy

### Level 1 - Quick Check (before building)
`validate_node_minimal(nodeType, config)` - Required fields only (<100ms)

### Level 2 - Comprehensive (before building)
`validate_node_operation(nodeType, config, 'runtime')` - Full validation with fixes

### Level 3 - Complete (after building)
`validate_workflow(workflow)` - Connections, expressions, AI tools

### Level 4 - Post-Deployment
1. `n8n_validate_workflow({id})` - Validate deployed workflow
2. `n8n_autofix_workflow({id})` - Auto-fix common errors
3. `n8n_list_executions()` - Monitor execution status

## Response Format

### Initial Creation
```
[Silent tool execution in parallel]

Created workflow:
- Webhook trigger → Slack notification
- Configured: POST /webhook → #general channel

Validation: ✅ All checks passed
```

### Modifications
```
[Silent tool execution]

Updated workflow:
- Added error handling to HTTP node
- Fixed required Slack parameters

Changes validated successfully.
```

## Batch Operations

Use `n8n_update_partial_workflow` with multiple operations in a single call:

✅ GOOD - Batch multiple operations:
```json
n8n_update_partial_workflow({
  id: "wf-123",
  operations: [
    {type: "updateNode", nodeId: "slack-1", changes: {...}},
    {type: "updateNode", nodeId: "http-1", changes: {...}},
    {type: "cleanStaleConnections"}
  ]
})
```

❌ BAD - Separate calls:
```json
n8n_update_partial_workflow({id: "wf-123", operations: [{...}]})
n8n_update_partial_workflow({id: "wf-123", operations: [{...}]})
```

###   CRITICAL: addConnection Syntax

The `addConnection` operation requires **four separate string parameters**. Common mistakes cause misleading errors.

❌ WRONG - Object format (fails with "Expected string, received object"):
```json
{
  "type": "addConnection",
  "connection": {
    "source": {"nodeId": "node-1", "outputIndex": 0},
    "destination": {"nodeId": "node-2", "inputIndex": 0}
  }
}
```

❌ WRONG - Combined string (fails with "Source node not found"):
```json
{
  "type": "addConnection",
  "source": "node-1:main:0",
  "target": "node-2:main:0"
}
```

✅ CORRECT - Four separate string parameters:
```json
{
  "type": "addConnection",
  "source": "node-id-string",
  "target": "target-node-id-string",
  "sourcePort": "main",
  "targetPort": "main"
}
```

**Reference**: [GitHub Issue #327](https://github.com/czlonkowski/n8n-mcp/issues/327)

### ⚠️ CRITICAL: IF Node Multi-Output Routing

IF nodes have **two outputs** (TRUE and FALSE). Use the **`branch` parameter** to route to the correct output:

✅ CORRECT - Route to TRUE branch (when condition is met):
```json
{
  "type": "addConnection",
  "source": "if-node-id",
  "target": "success-handler-id",
  "sourcePort": "main",
  "targetPort": "main",
  "branch": "true"
}
```

✅ CORRECT - Route to FALSE branch (when condition is NOT met):
```json
{
  "type": "addConnection",
  "source": "if-node-id",
  "target": "failure-handler-id",
  "sourcePort": "main",
  "targetPort": "main",
  "branch": "false"
}
```

**Common Pattern** - Complete IF node routing:
```json
n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [
    {type: "addConnection", source: "If Node", target: "True Handler", sourcePort: "main", targetPort: "main", branch: "true"},
    {type: "addConnection", source: "If Node", target: "False Handler", sourcePort: "main", targetPort: "main", branch: "false"}
  ]
})
```

**Note**: Without the `branch` parameter, both connections may end up on the same output, causing logic errors!

### removeConnection Syntax

Use the same four-parameter format:
```json
{
  "type": "removeConnection",
  "source": "source-node-id",
  "target": "target-node-id",
  "sourcePort": "main",
  "targetPort": "main"
}
```

## Example Workflow

### Template-First Approach

```
// STEP 1: Template Discovery (parallel execution)
[Silent execution]
search_templates_by_metadata({
  requiredService: 'slack',
  complexity: 'simple',
  targetAudience: 'marketers'
})
get_templates_for_task('slack_integration')

// STEP 2: Use template
get_template(templateId, {mode: 'full'})
validate_workflow(workflow)

// Response after all tools complete:
"Found template by **David Ashby** (@cfomodz).
View at: https://n8n.io/workflows/2414

Validation: ✅ All checks passed"
```

### Building from Scratch (if no template)

```
// STEP 1: Discovery (parallel execution)
[Silent execution]
search_nodes({query: 'slack', includeExamples: true})
list_nodes({category: 'communication'})

// STEP 2: Configuration (parallel execution)
[Silent execution]
get_node_essentials('n8n-nodes-base.slack', {includeExamples: true})
get_node_essentials('n8n-nodes-base.webhook', {includeExamples: true})

// STEP 3: Validation (parallel execution)
[Silent execution]
validate_node_minimal('n8n-nodes-base.slack', config)
validate_node_operation('n8n-nodes-base.slack', fullConfig, 'runtime')

// STEP 4: Build
// Construct workflow with validated configs
// ⚠️ Set ALL parameters explicitly

// STEP 5: Validate
[Silent execution]
validate_workflow(workflowJson)

// Response after all tools complete:
"Created workflow: Webhook → Slack
Validation: ✅ Passed"
```

### Batch Updates

```json
// ONE call with multiple operations
n8n_update_partial_workflow({
  id: "wf-123",
  operations: [
    {type: "updateNode", nodeId: "slack-1", changes: {position: [100, 200]}},
    {type: "updateNode", nodeId: "http-1", changes: {position: [300, 200]}},
    {type: "cleanStaleConnections"}
  ]
})
```

## Important Rules

### Core Behavior
1. **Silent execution** - No commentary between tools
2. **Parallel by default** - Execute independent operations simultaneously
3. **Templates first** - Always check before building (2,709 available)
4. **Multi-level validation** - Quick check → Full validation → Workflow validation
5. **Never trust defaults** - Explicitly configure ALL parameters

### Attribution & Credits
- **MANDATORY TEMPLATE ATTRIBUTION**: Share author name, username, and n8n.io link
- **Template validation** - Always validate before deployment (may need updates)

### Performance
- **Batch operations** - Use diff operations with multiple changes in one call
- **Parallel execution** - Search, validate, and configure simultaneously
- **Template metadata** - Use smart filtering for faster discovery

### Code Node Usage
- **Avoid when possible** - Prefer standard nodes
- **Only when necessary** - Use code node as last resort
- **AI tool capability** - ANY node can be an AI tool (not just marked ones)

### Most Popular n8n Nodes (for get_node_essentials):

1. **n8n-nodes-base.code** - JavaScript/Python scripting
2. **n8n-nodes-base.httpRequest** - HTTP API calls
3. **n8n-nodes-base.webhook** - Event-driven triggers
4. **n8n-nodes-base.set** - Data transformation
5. **n8n-nodes-base.if** - Conditional routing
6. **n8n-nodes-base.manualTrigger** - Manual workflow execution
7. **n8n-nodes-base.respondToWebhook** - Webhook responses
8. **n8n-nodes-base.scheduleTrigger** - Time-based triggers
9. **@n8n/n8n-nodes-langchain.agent** - AI agents
10. **n8n-nodes-base.googleSheets** - Spreadsheet integration
11. **n8n-nodes-base.merge** - Data merging
12. **n8n-nodes-base.switch** - Multi-branch routing
13. **n8n-nodes-base.telegram** - Telegram bot integration
14. **@n8n/n8n-nodes-langchain.lmChatOpenAi** - OpenAI chat models
15. **n8n-nodes-base.splitInBatches** - Batch processing
16. **n8n-nodes-base.openAi** - OpenAI legacy node
17. **n8n-nodes-base.gmail** - Email automation
18. **n8n-nodes-base.function** - Custom functions
19. **n8n-nodes-base.stickyNote** - Workflow documentation
20. **n8n-nodes-base.executeWorkflowTrigger** - Sub-workflow calls

**Note:** LangChain nodes use the `@n8n/n8n-nodes-langchain.` prefix, core nodes use `n8n-nodes-base.`

## n8n Skills System

This project uses the **n8n-skills** system - a collection of 7 expert skills designed to provide specialized guidance when building n8n workflows. These skills are installed in `~/.claude/skills/` and activate automatically when relevant.

### Available Skills

1. **n8n-code-javascript**
   - Write JavaScript code in n8n Code nodes
   - Use when: Writing JavaScript, using $input/$json/$node syntax, making HTTP requests with $helpers, working with dates using DateTime, troubleshooting Code node errors

2. **n8n-code-python**
   - Write Python code in n8n Code nodes (use JavaScript for 95% of cases)
   - Use when: Writing Python in n8n, using _input/_json/_node syntax, working with standard library

3. **n8n-expression-syntax**
   - Validate n8n expression syntax and fix common errors
   - Use when: Writing n8n expressions, using {{}} syntax, accessing $json/$node variables, troubleshooting expression errors, working with webhook data

4. **n8n-mcp-tools-expert**
   - Expert guide for using n8n-mcp MCP tools effectively
   - Use when: Searching for nodes, validating configurations, accessing templates, managing workflows, or using any n8n-mcp tool
   - Provides tool selection guidance, parameter formats, and common patterns

5. **n8n-node-configuration**
   - Operation-aware node configuration guidance
   - Use when: Configuring nodes, understanding property dependencies, determining required fields, choosing between get_node_essentials and get_node_info

6. **n8n-validation-expert**
   - Interpret validation errors and guide fixing them
   - Use when: Encountering validation errors, validation warnings, false positives, operator structure issues
   - Also helpful for understanding validation profiles, error types, or the validation loop process

7. **n8n-workflow-patterns**
   - Proven workflow architectural patterns from real n8n workflows
   - Use when: Building new workflows, designing workflow structure, choosing workflow patterns, planning workflow architecture
   - Covers: Webhook processing, HTTP API integration, database operations, AI agent workflows, scheduled tasks

### Skill Activation

Skills activate automatically when queries match their description triggers:
- "How do I write n8n expressions?" → n8n-expression-syntax skill
- "Find me a Slack node" → n8n-mcp-tools-expert skill
- "Build a webhook workflow" → n8n-workflow-patterns skill

You can also manually invoke skills using the Skill tool when needed.

### Cross-Skill Integration

Skills are designed to work together in a progressive workflow:
1. Use **n8n-workflow-patterns** to identify structure
2. Use **n8n-mcp-tools-expert** to find nodes
3. Use **n8n-node-configuration** for setup
4. Use **n8n-expression-syntax** for data mapping
5. Use **n8n-validation-expert** to validate

### Data-Driven Design

These skills are based on telemetry analysis of real n8n-mcp usage:
- **447,557** MCP tool usage events analyzed
- **31,917** workflows created
- **19,113** validation errors tracked
- **15,107** validation feedback loops

### Common Tool Usage Patterns (from Telemetry)

**Most Common Discovery Pattern:**
```
search_nodes → get_node_essentials (9,835 occurrences, 18s avg)
```

**Most Common Validation Pattern:**
```
n8n_update_partial_workflow → n8n_validate_workflow (7,841 occurrences)
Avg 23s thinking, 58s fixing
```

**Most Used Tool:**
```
n8n_update_partial_workflow (38,287 uses, 99.0% success)
Avg 56 seconds between edits
```

### Skill System Credits

The n8n-skills system was conceived by **Romuald Członkowski** - [AI Advisors](https://www.aiadvisors.pl/en)

Part of the n8n-mcp project: https://github.com/czlonkowski/n8n-skills

## Important File Locations

- Main spec: `docs/slovak-gossip-automation-spec (1).md` (75KB detailed technical specification)
- Environment variables: `.env.local` (contains N8N_APIKEY)
- n8n workflows: Store as JSON in version control (export from n8n UI)
- n8n-skills reference: `n8n-skills/` directory (cloned for reference, skills installed in `~/.claude/skills/`)

## n8n MCP Integration

This project is designed to be developed using n8n-MCP server for Claude Code:
- Use n8n-mcp tools to build and manage workflows
- Reference the detailed spec document for implementation guidance
- N8N_API_KEY is already configured in .env.local
- n8n instance URL needed for MCP setup (likely http://localhost:5678 for local dev)
- The 7 n8n-skills are installed and activate automatically when relevant

## Key Design Principles

1. **Modular**: Easy to swap sources, models, platforms
2. **Quality-driven**: Dynamic strictness based on queue size
3. **Cost-optimized**: Caching, conditional generation, parallel processing
4. **Data-driven**: Track model performance and engagement metrics
5. **Feedback loop**: Performance metrics inform future judging decisions
