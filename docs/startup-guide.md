# Startup Guide

## Prereqs

- Python 3.12+
- Supabase project credentials in `.env.local`

Required env vars:

```
SUPABASE_URL=...
SUPABASE_KEY=...
```

Optional (TTS providers):

```
ENABLE_TTS=true
TTS_PROVIDER=openai     # or "inworld"
TTS_MAX_CHARS=2000      # Inworld max chars; OpenAI can use 3500+
INWORLD_API_KEY=...     # Base64 API key from Inworld portal (for TTS)
INWORLD_BASE64_KEY=...  # Alias if you stored the key under this name
INWORLD_TTS_MODEL=inworld-tts-1.5-max
INWORLD_TTS_BASE_URL=https://api.inworld.ai
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

## Server access (Hetzner)

SSH from your local machine:

```
ssh -i "$env:USERPROFILE\\.ssh\\id_ed25519_hetzner" root@46.224.232.56
```

Move into the repo + activate venv:

```
cd /root/OnePlace
source .venv/bin/activate
```

Check service status:

```
systemctl status oneplace-api.service --no-pager
systemctl list-timers --all | grep oneplace
```

Logs:

```
tail -n 50 /var/log/oneplace/pipeline.log
```

Admin UI (basic auth):

```
http://46.224.232.56/
```
