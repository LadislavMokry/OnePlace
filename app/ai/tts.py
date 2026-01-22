from pathlib import Path
import base64

import requests

from app.ai.openai_client import OpenAIClient
from app.config import get_settings


def _inworld_tts(text: str, voice: str) -> bytes:
    settings = get_settings()
    if not settings.inworld_api_key:
        raise RuntimeError("INWORLD_API_KEY not set")
    base = settings.inworld_tts_base_url.rstrip("/")
    url = f"{base}/tts/v1/voice"
    payload = {
        "text": text,
        "voiceId": voice,
        "modelId": settings.inworld_tts_model,
    }
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Basic {settings.inworld_api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=settings.request_timeout,
    )
    resp.raise_for_status()
    data = resp.json() or {}
    audio_b64 = data.get("audioContent")
    if not audio_b64:
        raise RuntimeError("Inworld TTS response missing audioContent")
    return base64.b64decode(audio_b64)


def generate_voiceover(text: str, output_path: Path, voice: str = "alloy") -> Path:
    settings = get_settings()
    if not settings.enable_tts:
        raise RuntimeError("ENABLE_TTS is false")
    provider = (settings.tts_provider or "openai").lower()
    if provider == "inworld":
        audio_bytes = _inworld_tts(text, voice)
    else:
        client = OpenAIClient()
        audio_bytes = client.tts(settings.tts_model, voice, text)
    output_path.write_bytes(audio_bytes)
    return output_path
