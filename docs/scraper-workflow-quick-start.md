# Sub-Workflow 1A: Scraper - Quick Start Guide

**Last Updated**: 2025-11-03
**Est. Build Time**: 1-2 hours
**Difficulty**: Beginner-Intermediate

---

## 📋 Overview

This workflow scrapes **5 Slovak celebrity news websites** every hour and stores the raw HTML content in Supabase for later processing.

**What it does**:
- Runs every hour (cron: `0 * * * *`)
- Scrapes 5 Slovak celebrity news sites in parallel
- Stores raw HTML in Supabase `articles` table
- Continues if individual sources fail (minimum 3/5 required)
- Automatic deduplication via UNIQUE constraint on `source_url`

**Architecture**:
```
Schedule Trigger (hourly)
    → HTTP Request (5 parallel branches)
        → IF Node (check HTTP 200)
            → Supabase Insert (with deduplication)
```

---

## ✅ Pre-Build Checklist (5 minutes)

Before starting, verify:

- [ ] **Supabase** database set up
  - [ ] `articles` table exists (run `db/supabase-schema.sql` if not)
  - [ ] Supabase URL and API key in `.env.local`

- [ ] **n8n** instance ready
  - [ ] n8n running at http://localhost:5678
  - [ ] Supabase credential created (name: "Supabase account", ID: `woAUTvWByiJ9u8p2`)

- [ ] **Environment** variables
  - [ ] `SUPABASE_URL` = `https://ftlwysaeliivaukqozbs.supabase.co`
  - [ ] `SUPABASE_KEY` = anon/public key (check `.env.local`)

**Verify Supabase connection**:
```sql
-- Run in Supabase SQL Editor
SELECT COUNT(*) FROM articles;
-- Should return 0 (or existing count if you've tested before)
```

---

## 🌐 Data Sources - Celebrity News URLs

### 1. **Topky.sk** (Prominenti)
**Base URL**: `https://www.topky.sk`
**Celebrity Sections** (choose best performing):
- **Primary**: `/se/15/Prominenti` (main celebrities hub)
- **Domestic**: `/se/100313/Domaci-prominenti` (Slovak celebrities)
- **International**: `/se/100314/Zahranicni-prominenti` (foreign celebrities)
- **Showbiz**: `/se/1005367/SOUBIZNIS-Kvizy-o-celebritach-a-osobnostiach`

**Recommended**: Start with `/se/15/Prominenti`

---

### 2. **Čas.sk** (Prominenti)
**Base URL**: `https://www.cas.sk`
**Celebrity Section**: `/r/prominenti`

**Full URL**: `https://www.cas.sk/r/prominenti`

---

### 3. **Pluska.sk** (Šoubiznis)
**Base URL**: `https://www1.pluska.sk`
**Celebrity Section**: `/r/soubiznis`

**Full URL**: `https://www1.pluska.sk/r/soubiznis`

---

### 4. **Refresher.sk** (Osobnosti)
**Base URL**: `https://refresher.sk`
**Celebrity Sections** (choose best performing):
- **Primary**: `/osobnosti` (personalities/celebrities - main section)
- **Alternative**: `/kultura` (culture/entertainment - broader)

**Recommended**: Start with `/osobnosti`

---

### 5. **Startitup.sk** (Kultúra)
**Base URL**: `https://www.startitup.sk`
**Celebrity Section**:
- **Primary**: `/kategoria/kultura/` (culture/entertainment)
- **Alternative**: `/kategoria/zaujimavosti/` (interesting stories - may include celebrity content)

**Recommended**: Start with `/kategoria/kultura/`

---

## 📦 Full URL List (Copy-Paste Ready)

```
https://www.topky.sk/se/15/Prominenti
https://www.cas.sk/r/prominenti
https://www1.pluska.sk/r/soubiznis
https://refresher.sk/osobnosti
https://www.startitup.sk/kategoria/kultura/
```

✅ **All 5 URLs verified and ready to use!**

---

## 🔧 HTTP Request Node Configuration

### **Template Configuration (Copy for Each Source)**

```json
{
  "method": "GET",
  "url": "https://www.topky.sk/se/15/Prominenti",
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "sk-SK,sk;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br"
  },
  "timeout": 30000,
  "ignoreSSLIssues": false,
  "followRedirects": true
}
```

### **Per-Source Configurations**

#### **Source 1: Topky.sk**
```json
{
  "method": "GET",
  "url": "https://www.topky.sk/se/15/Prominenti",
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html",
    "Accept-Language": "sk-SK,sk;q=0.9"
  },
  "timeout": 30000
}
```

#### **Source 2: Čas.sk**
```json
{
  "method": "GET",
  "url": "https://www.cas.sk/r/prominenti",
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html",
    "Accept-Language": "sk-SK,sk;q=0.9"
  },
  "timeout": 30000
}
```

#### **Source 3: Pluska.sk**
```json
{
  "method": "GET",
  "url": "https://www1.pluska.sk/r/soubiznis",
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html",
    "Accept-Language": "sk-SK,sk;q=0.9"
  },
  "timeout": 30000
}
```

#### **Source 4: Refresher.sk**
```json
{
  "method": "GET",
  "url": "https://refresher.sk/osobnosti",
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html",
    "Accept-Language": "sk-SK,sk;q=0.9"
  },
  "timeout": 30000
}
```

#### **Source 5: Startitup.sk**
```json
{
  "method": "GET",
  "url": "https://www.startitup.sk/kategoria/kultura/",
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html",
    "Accept-Language": "sk-SK,sk;q=0.9"
  },
  "timeout": 30000
}
```

---

## 🗄️ Supabase Insert Node - Field Mappings

### **Configuration**:
- **Resource**: Row
- **Operation**: Create
- **Table**: articles
- **Data Mode**: Define Below for Each Column

### **Field Mappings** (Copy-Paste):

| Field Name | Field Value (n8n Expression) | Notes |
|------------|------------------------------|-------|
| `source_url` | `={{ $json.url }}` | From HTTP Request response |
| `source_website` | Hardcode per source (see below) | Static value per HTTP node |
| `raw_html` | `={{ $json.body }}` | Full HTML response |
| `scraped_at` | `={{ $now }}` | Current timestamp |

### **Source Website Values** (Hardcoded per Source):

- **Source 1 (Topky)**: `topky.sk`
- **Source 2 (Čas)**: `cas.sk`
- **Source 3 (Pluska)**: `pluska.sk`
- **Source 4 (Refresher)**: `refresher.sk`
- **Source 5 (Startitup)**: `startitup.sk`

### **Complete Example for Topky.sk**:

```
Field 1:
  Name: source_url
  Value: ={{ $json.url }}

Field 2:
  Name: source_website
  Value: topky.sk

Field 3:
  Name: raw_html
  Value: ={{ $json.body }}

Field 4:
  Name: scraped_at
  Value: ={{ $now }}
```

**⚠️ Important**:
- Leave other fields (`title`, `content`, `summary`, `judge_score`, etc.) empty - they'll be filled by later workflows
- The `id` field auto-generates (UUID)
- The `processed` and `scored` fields default to `FALSE`

---

## 🚧 Step-by-Step Build Instructions

### **Step 1: Create New Workflow in n8n**

1. Open http://localhost:5678
2. Click **"+ New workflow"**
3. Name it: **"Scraper - Hourly Data Collection"**
4. Save

---

### **Step 2: Add Schedule Trigger**

1. Click **"+"** → Search "Schedule Trigger"
2. Configure:
   - **Mode**: Every Hour
   - **Cron Expression**: `0 * * * *`
   - **Alternative**: Use built-in "Every Hour" option
3. Click **"Execute Node"** to test (should return timestamp)

---

### **Step 3: Add HTTP Request Nodes (5 Sources)**

For **EACH** of the 5 sources:

1. Click **"+"** → Search "HTTP Request"
2. Name it: `HTTP Request - [Source Name]` (e.g., "HTTP Request - Topky")
3. Configure:
   - **Method**: GET
   - **URL**: Copy from "Full URL List" above
   - **Authentication**: None
   - **Response** → **Response Format**: String (to get raw HTML)
4. Click **"Add Header"**:
   - **Name**: `User-Agent`
   - **Value**: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`
5. Click **"Add Header"**:
   - **Name**: `Accept`
   - **Value**: `text/html`
6. **Options** → **Timeout**: 30000

**Repeat for all 5 sources!**

---

### **Step 4: Add IF Nodes (Error Handling)**

For **EACH** HTTP Request node:

1. Click **"+"** after HTTP Request → Search "IF"
2. Name it: `IF - Check [Source] Status`
3. Configure:
   - **Condition**: Number
   - **Value 1**: `={{ $json.statusCode }}`
   - **Operation**: Equal
   - **Value 2**: `200`
4. This creates **two branches**:
   - **True** (green) = Success, continue to Supabase
   - **False** (red) = Failure, skip insertion

---

### **Step 5: Add Supabase Insert Nodes**

For **EACH** IF node (connect to TRUE branch):

1. Click **"+"** on **TRUE output** → Search "Supabase"
2. Name it: `Supabase Insert - [Source]`
3. Configure:
   - **Credential**: Select "Supabase account"
   - **Resource**: Row
   - **Operation**: Create
   - **Table**: articles
   - **Data Mode**: Define Below for Each Column
4. Click **"Add Field"** 4 times and configure:
   - **Field 1**: `source_url` = `={{ $json.url }}`
   - **Field 2**: `source_website` = `topky.sk` (hardcode per source)
   - **Field 3**: `raw_html` = `={{ $json.body }}`
   - **Field 4**: `scraped_at` = `={{ $now }}`
5. **Settings** → **Continue On Fail**: Enable (checkmark)

**Repeat for all 5 sources!**

---

### **Step 6: Connect Nodes**

Create connections:

```
Schedule Trigger
    ├─→ HTTP Request - Topky
    │       └─→ IF - Check Topky Status
    │               ├─→ (TRUE) Supabase Insert - Topky
    │               └─→ (FALSE) [End]
    │
    ├─→ HTTP Request - Cas
    │       └─→ IF - Check Cas Status
    │               ├─→ (TRUE) Supabase Insert - Cas
    │               └─→ (FALSE) [End]
    │
    ├─→ HTTP Request - Pluska
    │       └─→ IF - Check Pluska Status
    │               ├─→ (TRUE) Supabase Insert - Pluska
    │               └─→ (FALSE) [End]
    │
    ├─→ HTTP Request - Refresher
    │       └─→ IF - Check Refresher Status
    │               ├─→ (TRUE) Supabase Insert - Refresher
    │               └─→ (FALSE) [End]
    │
    └─→ HTTP Request - Startitup
            └─→ IF - Check Startitup Status
                    ├─→ (TRUE) Supabase Insert - Startitup
                    └─→ (FALSE) [End]
```

**To connect**:
1. Drag from Schedule Trigger output to each HTTP Request input (creates 5 parallel branches)
2. Connect each HTTP Request to its corresponding IF node
3. Connect IF TRUE output to Supabase Insert
4. Leave IF FALSE output unconnected (workflow ends)

---

### **Step 7: Test Manually**

1. Click **"Execute Workflow"** (bottom button)
2. Watch all 5 branches execute in parallel
3. Check results:
   - ✅ HTTP nodes should return status 200
   - ✅ IF nodes should route to TRUE branch
   - ✅ Supabase Insert nodes should succeed
   - ⚠️ If any source fails (404, timeout, etc.), IF routes to FALSE (expected behavior)

---

### **Step 8: Verify Data in Supabase**

1. Go to Supabase dashboard → Database → Table Editor
2. Open `articles` table
3. You should see 3-5 new rows (depending on how many sources succeeded)
4. Check columns:
   - `source_url` = Full URL of scraped page
   - `source_website` = Domain name (topky.sk, etc.)
   - `raw_html` = Long HTML string
   - `scraped_at` = Recent timestamp
   - `processed` = `false`
   - `scored` = `false`

**SQL Verification Query**:
```sql
SELECT
  source_website,
  COUNT(*) as article_count,
  MAX(scraped_at) as last_scraped
FROM articles
GROUP BY source_website
ORDER BY article_count DESC;
```

Expected output:
```
source_website | article_count | last_scraped
---------------|---------------|------------------
topky.sk       | 1             | 2025-11-03 14:00
refresher.sk   | 1             | 2025-11-03 14:00
startitup.sk   | 1             | 2025-11-03 14:00
cas.sk         | 1             | 2025-11-03 14:00 (if URL verified)
pluska.sk      | 1             | 2025-11-03 14:00 (if URL verified)
```

---

### **Step 9: Test Deduplication**

1. Click **"Execute Workflow"** again (run twice)
2. Check Supabase `articles` table
3. Should still have ~5 rows (not 10)
4. If you see duplicates, check:
   - UNIQUE constraint on `source_url` exists
   - Supabase Insert has "Upsert" mode enabled (should skip duplicates)

**SQL Query to Check Duplicates**:
```sql
SELECT source_url, COUNT(*) as duplicates
FROM articles
GROUP BY source_url
HAVING COUNT(*) > 1;
```

Expected: **No results** (no duplicates)

---

### **Step 10: Activate Workflow**

1. Click **"Active"** toggle (top right, currently OFF)
2. Workflow will now run every hour automatically
3. **First execution**: Exact top of the hour (e.g., 14:00:00, 15:00:00, etc.)

---

## 🧪 Testing & Validation

### **Test Checklist**:

- [ ] **Functional**: All 5 HTTP nodes execute successfully
- [ ] **Error Handling**: Workflow continues if 1-2 sources fail (test by using invalid URL)
- [ ] **Data Storage**: Articles stored in Supabase `articles` table
- [ ] **Deduplication**: Running twice doesn't create duplicates
- [ ] **Scheduling**: Workflow runs every hour automatically (after activation)
- [ ] **Minimum Success**: At least 3/5 sources succeed per execution

### **Manual Testing Scenarios**:

#### **Test 1: Happy Path (All Sources Work)**
1. Verify all 5 URLs are valid
2. Execute workflow manually
3. Expect: 5 articles inserted into Supabase

#### **Test 2: Single Source Failure**
1. Change one HTTP Request URL to invalid (e.g., `https://invalid-site-12345.sk`)
2. Execute workflow
3. Expect: 4 articles inserted, 1 IF node routes to FALSE, workflow succeeds

#### **Test 3: Deduplication**
1. Execute workflow twice in a row
2. Expect: Same 5 articles, no duplicates (UNIQUE constraint works)

#### **Test 4: Timeout Handling**
1. Change timeout to 1ms on one HTTP node
2. Execute workflow
3. Expect: That source times out, others continue

---

## 🔍 Monitoring & Verification

### **Supabase Dashboard Queries**:

#### **Check Latest Scrapes**:
```sql
SELECT
  id,
  source_website,
  scraped_at,
  LENGTH(raw_html) as html_size_bytes
FROM articles
ORDER BY scraped_at DESC
LIMIT 20;
```

#### **Count Articles Per Source**:
```sql
SELECT
  source_website,
  COUNT(*) as total_articles,
  MAX(scraped_at) as last_scraped,
  MIN(scraped_at) as first_scraped
FROM articles
GROUP BY source_website
ORDER BY total_articles DESC;
```

#### **Check for Errors (Empty HTML)**:
```sql
SELECT
  source_website,
  source_url,
  scraped_at
FROM articles
WHERE raw_html IS NULL OR raw_html = '' OR LENGTH(raw_html) < 100
ORDER BY scraped_at DESC;
```

#### **Scraping Success Rate (Last 24 Hours)**:
```sql
SELECT
  DATE_TRUNC('hour', scraped_at) as hour,
  source_website,
  COUNT(*) as articles_scraped
FROM articles
WHERE scraped_at > NOW() - INTERVAL '24 hours'
GROUP BY hour, source_website
ORDER BY hour DESC, source_website;
```

---

## 🐛 Troubleshooting

### **Issue 1: HTTP 403 Forbidden**
**Symptom**: HTTP Request returns status 403
**Cause**: Website blocking requests with generic User-Agent
**Fix**:
1. Update User-Agent header to real browser string (already in template)
2. Add more headers (Accept-Language, Referer)
3. Try different User-Agent if still fails

---

### **Issue 2: HTTP Timeout**
**Symptom**: HTTP Request fails with timeout error
**Cause**: Website slow or down
**Fix**:
1. Increase timeout to 60000ms (60 seconds)
2. Check website is accessible in browser
3. If persistent, consider removing that source

---

### **Issue 3: Duplicate Key Violation**
**Symptom**: Supabase Insert fails with "duplicate key" error
**Cause**: UNIQUE constraint on `source_url`
**Fix**:
- This is **expected behavior** (deduplication working!)
- Enable "Continue On Fail" on Supabase Insert node (already in template)
- Workflow should continue despite error

---

### **Issue 4: Empty HTML Response**
**Symptom**: `raw_html` field is empty or very short (<100 characters)
**Cause**: Website returned error page or redirect
**Fix**:
1. Check `statusCode` in HTTP node output (should be 200)
2. Verify URL in browser (may have changed)
3. Check if website uses JavaScript rendering (requires different approach)

---

### **Issue 5: All Sources Fail**
**Symptom**: All 5 IF nodes route to FALSE
**Cause**: Network issue or n8n configuration problem
**Fix**:
1. Check internet connection
2. Try accessing URLs in browser
3. Check n8n firewall/proxy settings
4. Verify Supabase credentials are correct

---

### **Issue 6: Supabase Insert Fails with "relation does not exist"**
**Symptom**: Error message: `relation "articles" does not exist`
**Cause**: `articles` table not created in Supabase
**Fix**:
1. Go to Supabase SQL Editor
2. Run `db/supabase-schema.sql` script (creates all 4 tables)
3. Verify table exists: `SELECT * FROM articles LIMIT 1;`

---

### **Issue 7: Field Mapping Errors**
**Symptom**: Supabase Insert fails with "column does not exist"
**Cause**: Field name typo or incorrect column name
**Fix**:
1. Check exact field names in Supabase (case-sensitive):
   - `source_url` (not `sourceUrl` or `source_URL`)
   - `source_website` (not `source_site`)
   - `raw_html` (not `rawHtml` or `html`)
   - `scraped_at` (not `scrapedAt` or `created_at`)
2. Verify dropdown shows correct field names (Supabase node fetches schema)

---

## 📊 Success Criteria

After activation, the workflow should:

- ✅ **Execute automatically** every hour on the hour
- ✅ **Store articles** from at least 3/5 sources per execution
- ✅ **No duplicates** in database (UNIQUE constraint working)
- ✅ **Continue on failure** (individual source failures don't crash workflow)
- ✅ **Fast execution** (<60 seconds for all 5 sources in parallel)

**After 24 hours**, you should have:
- **72-120 articles** in Supabase (3-5 per hour × 24 hours)
- **All 5 sources** represented (or at least 3 if some are problematic)
- **No errors** in n8n execution history (or only expected "duplicate key" warnings)

---

## 📈 Performance Expectations

### **Execution Time**:
- **Per HTTP Request**: 1-5 seconds (depends on website)
- **Total Workflow**: 5-15 seconds (parallel execution)
- **Supabase Insert**: <1 second per row

### **Data Volume**:
- **Per Article HTML**: 50KB - 200KB (raw HTML)
- **Per Hour**: 250KB - 1MB (5 articles)
- **Per Day**: 6MB - 24MB (72-120 articles)
- **Per Week**: 42MB - 168MB

**Supabase Free Tier**: 500MB database storage (sufficient for ~20,000-40,000 articles)

---

## 🚀 Next Steps

Once this workflow is stable:

1. **Monitor for 24 hours** - Verify hourly execution and data quality
2. **Optimize URLs** - Replace underperforming sources with better ones
3. **Build Sub-Workflow 1B** - Extraction (HTML → Summary with GPT-5 Nano)
4. **Build Sub-Workflow 1C** - First Judge (Score articles 1-10)

---

## 📚 Reference Files

- **Full Spec**: `docs/slovak-gossip-automation-spec (1).md` (Component 1)
- **Implementation Plan**: `docs/implementation-plan.md` (Phase 1, Sub-Workflow 1A)
- **Task List**: `docs/todo.md` (89 granular tasks for this workflow)
- **Database Schema**: `db/supabase-schema.sql` (articles table definition)

---

*Created: 2025-11-03*
*For: Slovak Celebrity Gossip Content Automation System*
*Workflow: Sub-Workflow 1A - Scraper (Hourly Data Collection)*
