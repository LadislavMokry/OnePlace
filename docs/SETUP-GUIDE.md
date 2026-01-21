# Setup Guide - Supabase + Python API
Update Notice (2025-12-30): The project now uses a Python-first architecture (FastAPI + worker). n8n instructions below are legacy reference only.
Update Notice (2026-01-05): `.env` / `.env.local` are auto-loaded for Python workers; place OpenAI keys and model settings there.
See `docs/python-spec.md` and `docs/python-todo.md` for the current plan.

## Step 1: Identify Which Keys to Use

### ✅ **Use the `anon` / `public` Key** (Recommended)

**Why?**
- Row-level security (RLS) enforced (when you set it up)
- Safe for n8n workflows
- Full read/write access with your RLS policies
- This is what most n8n workflows should use

**When to use `service_role` / `secret` key:**
- Only if you need to bypass RLS policies
- For admin operations (bulk deletes, schema changes)
- Keep this key VERY secure (never expose publicly)

---

## Step 2: Get Your Supabase Credentials

### **Option A: Using Legacy Keys (Recommended for n8n)**

1. Go to your Supabase project dashboard
2. Click **Settings** → **API**
3. Under **Project API keys**, you'll see:

```
Project URL
https://xxxxxxxxxxxxx.supabase.co
👆 Copy this

anon public
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
👆 Copy this (use for SUPABASE_KEY)

service_role
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
👆 DON'T use this unless you need admin access
```

### **Option B: Using New Project-Specific Keys**

If you see these instead:
```
publishable key (same as anon/public)
secret key (same as service_role)
```

**Use the `publishable` key** for n8n workflows.

---

## Step 3: Update .env.local

Add these lines to your `.env.local` file:

```bash
# Existing
N8N_API_KEY=your_n8n_api_key_here

# Phase 1 Keys (Add these)
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...  # Use anon/public key here
OPENAI_API_KEY=sk-...

# Optional: Store service_role separately (for admin operations)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...  # Keep this VERY secure
```

**Important:**
- Use `anon` / `public` key (or `publishable` key) for `SUPABASE_KEY`
- **Do NOT** use `service_role` / `secret` key unless you specifically need admin access
- The `anon` key is safe to use in n8n because n8n server is a trusted environment

---

## Step 4: Test Connection (Python API)

### **Start the API**
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### **Health Check**
```bash
curl http://localhost:8000/health
```
Expected:
```json
{"status":"ok"}
```

### **Test Intake (Text)**
```bash
curl -X POST http://localhost:8000/intake/text \
  -H "Content-Type: application/json" \
  -d '{"title":"Sample","text":"Chapter 1\nHello"}'
```

---

## Legacy: Test Connection in n8n

### **Method 1: Manual Test in n8n UI**

1. Open n8n at http://localhost:5678
2. Create a new workflow (click **+** button)
3. Add a **Manual Trigger** node
4. Add a **Supabase** node

#### **Configure Supabase Credentials:**

Click on **Supabase** node → **Credentials** dropdown → **Create New**

Fill in:
```
Credential Name: Supabase API
Host: https://xxxxxxxxxxxxx.supabase.co  (your SUPABASE_URL)
Service Role Secret: eyJhbGc...  (your SUPABASE_KEY - use anon/public key)
```

**⚠️ Confusing Naming Alert:**
The field is called "Service Role Secret" but you should paste your **`anon`/`public` key** here (not the actual service_role key). This is just poor naming by n8n.

Click **Save**.

#### **Test the Connection:**

1. Set **Operation** to **Get Many**
2. Set **Table** to **articles**
3. Click **Execute Node** (play button)

**Expected Result:**
```json
{
  "success": true,
  "data": []  // Empty array (no articles yet)
}
```

**If you see an error:**
- ❌ `"Invalid API key"` → Check that you copied the key correctly
- ❌ `"relation 'articles' does not exist"` → Run the SQL schema in Supabase
- ❌ `"Could not connect"` → Check that SUPABASE_URL is correct

---

### **Method 2: Import Test Workflow**

I've created a test workflow that will:
1. ✅ Insert a test article
2. ✅ Query all articles
3. ✅ Delete test articles (cleanup)

**To import:**

1. Open n8n at http://localhost:5678
2. Click **Workflows** → **Import from File**
3. Select `workflows/test-supabase-connection.json`
4. Open the imported workflow

**Configure credentials:**

1. Click on each Supabase node
2. Set credentials to your Supabase API credentials
3. Click **Save**

**Run the test:**

1. Click **Execute Workflow** (play button at bottom)
2. Watch the nodes execute in sequence
3. Check the output of each node

**Expected Output:**

**Supabase Insert Test:**
```json
{
  "id": "uuid-here",
  "source_url": "https://test.example.com/test-article-1234567890",
  "source_website": "test.sk",
  "title": "Test Article - Connection Verification",
  "raw_html": "<html><body>This is a test article...</body></html>",
  "processed": false,
  "scored": false,
  "created_at": "2025-11-03T12:00:00.000Z"
}
```

**Supabase Query Test:**
```json
[
  {
    "id": "uuid-here",
    "source_url": "https://test.example.com/test-article-1234567890",
    "source_website": "test.sk",
    "title": "Test Article - Connection Verification",
    ...
  }
]
```

**Supabase Cleanup Test:**
```json
{
  "success": true,
  "deleted": 1
}
```

**If all 3 nodes execute successfully: ✅ Your Supabase connection works!**

---

## Step 5: Verify Database Tables Exist

Go back to Supabase dashboard:

1. Click **Database** → **Tables** (left sidebar)
2. You should see 4 tables:
   - ✅ `articles`
   - ✅ `posts`
   - ✅ `performance_metrics`
   - ✅ `model_performance`

3. Click on **`articles`** table
4. You should see your test article (if you didn't run cleanup)

**If tables are missing:**
- Go to **SQL Editor**
- Run the entire `db/supabase-schema.sql` script
- Refresh the Tables view

---

## Step 6: Test OpenAI Connection (Optional)

Let's verify your OpenAI API key works:

1. In n8n, create a new workflow
2. Add **Manual Trigger** node
3. Add **OpenAI** node

**Configure OpenAI Credentials:**

Click on **OpenAI** node → **Credentials** → **Create New**

Fill in:
```
Credential Name: OpenAI API
API Key: sk-...  (your OPENAI_API_KEY)
```

Click **Save**.

**Test the Connection:**

1. Set **Resource** to **Text**
2. Set **Operation** to **Complete**
3. Set **Model** to **gpt-4o-mini** (cheapest model for testing)
4. Set **Prompt** to: `Say "Connection successful!" in Slovak`
5. Click **Execute Node**

**Expected Output:**
```json
{
  "text": "Pripojenie úspešné!"
}
```

**If you see an error:**
- ❌ `"Incorrect API key"` → Check your OPENAI_API_KEY
- ❌ `"Rate limit exceeded"` → Wait 1 minute and try again
- ❌ `"Model not found"` → Try a different model (gpt-4o, gpt-3.5-turbo)

---

## Common Issues & Solutions

### Issue 1: "Invalid API key" (Supabase)

**Solution:**
- Verify you copied the **entire** key (they're very long, ~200+ characters)
- Make sure there are no extra spaces at the beginning or end
- Try copying the key again from Supabase dashboard
- Confirm you're using the correct project (check project URL)

### Issue 2: "relation 'articles' does not exist"

**Solution:**
- Go to Supabase → SQL Editor
- Run the entire `db/supabase-schema.sql` script
- Wait 5 seconds for schema to propagate
- Try again

### Issue 3: "Could not connect to Supabase"

**Solution:**
- Check that your Supabase project is active (not paused)
- Verify SUPABASE_URL includes `https://` and ends with `.supabase.co`
- Check your internet connection
- Try accessing the URL in browser (should return `{"msg":"The server is running."}`)

### Issue 4: "Row-level security policy violation"

**Solution:**
- This means you have RLS enabled but no policies set
- **Option A**: Disable RLS for MVP (Settings → Database → Policies)
- **Option B**: Use `service_role` key (bypasses RLS, but less secure)
- **Option C**: Create RLS policies (for production)

**To disable RLS (for testing):**
```sql
-- Run in Supabase SQL Editor
ALTER TABLE articles DISABLE ROW LEVEL SECURITY;
ALTER TABLE posts DISABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics DISABLE ROW LEVEL SECURITY;
ALTER TABLE model_performance DISABLE ROW LEVEL SECURITY;
```

### Issue 5: OpenAI "Insufficient quota" or "Rate limit exceeded"

**Solution:**
- Check your OpenAI account has credits (https://platform.openai.com/usage)
- Add payment method if needed (Settings → Billing)
- Wait 1 minute if rate limited
- Use a cheaper model for testing (`gpt-4o-mini` instead of `gpt-4`)

---

## Next Steps After Successful Testing

Once you've verified:
- ✅ Supabase connection works (test workflow executes successfully)
- ✅ Database tables exist (4 tables visible in Supabase dashboard)
- ✅ OpenAI connection works (can generate text)

**You're ready to build the first workflow!**

Next, run:
1. **API Intake** (FastAPI) for manual uploads/paste
2. **Scraper Worker** (Python) for project sources
3. **AI Workers** (planned) for extraction/judging/generation

---

## Security Best Practices

### ✅ Do's:
- ✅ Use `anon`/`public` key for n8n workflows
- ✅ Store keys in `.env.local` (never commit to git)
- ✅ Add `.env.local` to `.gitignore`
- ✅ Use different keys for dev/staging/production
- ✅ Rotate keys if accidentally exposed

### ❌ Don'ts:
- ❌ Never use `service_role`/`secret` key unless necessary
- ❌ Never commit keys to git
- ❌ Never share keys in screenshots or logs
- ❌ Never hardcode keys in workflows (use credentials system)

---

## Quick Reference

### **What key should I use?**

| Use Case | Key to Use | Why |
|----------|-----------|-----|
| n8n workflows (general) | `anon` / `public` | Safe, RLS enforced |
| n8n workflows (admin) | `service_role` / `secret` | Bypasses RLS (use with caution) |
| Client-side apps | `anon` / `public` | Never expose service_role to clients |
| Server-side APIs | `service_role` / `secret` | Only if you need admin access |

### **For this project:**
👉 Use `anon` / `public` key in n8n (stored as `SUPABASE_KEY`)

---

*Last Updated: 2025-12-30*
