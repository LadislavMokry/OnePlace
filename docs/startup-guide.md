# Startup Guide

## Prereqs

- Python 3.12+
- Supabase project credentials in `.env.local`

Required env vars:

```
SUPABASE_URL=...
SUPABASE_KEY=...
```

## Install dependencies

```
python3 -m pip install -r requirements.txt
```

If your environment enforces PEP 668 and blocks installs, use:

```
python3 -m pip install -r requirements.txt --break-system-packages
```

## Start the API (local dev)

```
python -m uvicorn app.main:app --reload --port 8000
```

Open:

```
http://127.0.0.1:8000
```
