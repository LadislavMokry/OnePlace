# Postgres Credential Setup for n8n

This guide will help you set up PostgreSQL credentials in n8n to connect to your Supabase database.

## Step 1: Get Your Supabase PostgreSQL Credentials

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Navigate to **Settings** → **Database**
4. Scroll down to the **Connection string** section
5. You'll see a connection string that looks like this:

```
postgresql://postgres:[YOUR-PASSWORD]@db.your-project-ref.supabase.co:5432/postgres
```

From this string, extract the following values:

| Field    | Value                                      | Example                                |
|----------|-------------------------------------------|----------------------------------------|
| **Host** | `db.your-project-ref.supabase.co`         | `db.abcdefghijklmnop.supabase.co`      |
| **Port** | `5432` (default) or `6543` (pooler)       | `5432`                                 |
| **Database** | `postgres`                             | `postgres`                             |
| **User** | `postgres`                                 | `postgres`                             |
| **Password** | Your database password                  | (set when you created the project)     |

### Important Notes:

- **Password**: This is the password you set when you first created your Supabase project. If you forgot it, you can reset it in **Settings** → **Database** → **Database Password** → **Reset Database Password**
- **Connection Pooling**:
  - Use port `5432` for direct connection (recommended for n8n)
  - Use port `6543` for connection pooling (use if you have many concurrent connections)

## Step 2: Add Postgres Credentials in n8n

1. **Open your n8n instance** (http://localhost:5678 or your server URL)

2. **Go to Credentials**:
   - Click on your profile icon (top right)
   - Select **Credentials**

3. **Create New Credential**:
   - Click **+ Add Credential**
   - Search for **Postgres**
   - Select **Postgres account**

4. **Fill in the credential details**:

   ```
   Name: Supabase Postgres
   ```

   **Connection Details:**
   - **Host**: `db.your-project-ref.supabase.co` (from Step 1)
   - **Database**: `postgres`
   - **User**: `postgres`
   - **Password**: Your database password (from Step 1)
   - **Port**: `5432`

   **SSL:**
   - **SSL**: Enable this checkbox ✅
   - **SSL Mode**: `require` (Supabase requires SSL)

5. **Test the connection**:
   - Click **Test** button at the bottom
   - You should see: ✅ **Connection successful**

6. **Save the credential**:
   - Click **Save** button

## Step 3: Use the Credential in Your Workflow

After saving, your n8n workflows will automatically use this credential when you import them.

The credential is referenced in the workflow JSON like this:

```json
"credentials": {
  "postgres": {
    "id": "1",
    "name": "Supabase Postgres"
  }
}
```

When you import the workflow:
- n8n will prompt you to select a credential
- Choose the **"Supabase Postgres"** credential you just created
- The credential will be applied to all 5 Postgres nodes in the workflow

## Troubleshooting

### Error: "Connection refused"
- **Check**: Is your Supabase project active? (Not paused)
- **Check**: Is the host correct? Should be `db.xxx.supabase.co`
- **Check**: Is port `5432` open in your firewall?

### Error: "password authentication failed"
- **Solution**: Reset your database password in Supabase Dashboard → Settings → Database → Reset Database Password
- **Note**: This will NOT affect your Supabase API keys or existing data

### Error: "SSL required"
- **Solution**: Make sure **SSL** checkbox is enabled and **SSL Mode** is set to `require`

### Error: "database 'postgres' does not exist"
- **Check**: The database name should be lowercase `postgres` (not `Postgres`)

## Verification

After setup, verify the connection works:

1. Open your updated **Sub-Workflow 1A: Scraper - Hourly Data Collection**
2. Click on any **Postgres Upsert** node
3. You should see the credential selected
4. Click **Execute Node** (test with sample data)
5. If successful, you'll see the inserted/updated row data

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for passwords if deploying to production
3. **Rotate database passwords** regularly (every 90 days)
4. **Use read-only credentials** for workflows that only query data

## Additional Resources

- [Supabase Database Documentation](https://supabase.com/docs/guides/database)
- [n8n Postgres Node Documentation](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.postgres/)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)

---

**Need help?** Check the error messages in n8n's execution logs or consult the Supabase community forum.
