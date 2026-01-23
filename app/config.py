import os
from pathlib import Path

from dotenv import load_dotenv
from functools import lru_cache
from pydantic import BaseModel

# Load .env.local or .env from repo root if present (do not override real env).
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env.local", override=False)
load_dotenv(_ROOT / ".env", override=False)


class Settings(BaseModel):
    supabase_url: str
    supabase_key: str
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    manual_intake_script: str = "scripts/extract_text.py"
    manual_intake_dir: str | None = None
    max_words: int = 2500
    request_timeout: int = 30
    extraction_max_chars: int = 20000
    extraction_use_llm: bool = True
    extraction_model: str = "gpt-5-nano"
    judge_model: str = "gpt-4.1-mini"
    second_judge_model: str = "gpt-4.1-mini"
    generation_models: list[str] = ["gpt-4.1-mini"]
    generation_variants: int = 3
    video_min_score: int = 6
    audio_roundup_model: str = "gpt-5-mini"
    audio_roundup_size: int = 8
    audio_roundup_hours: int = 24
    audio_roundup_voice_a: str = "onyx"
    audio_roundup_voice_b: str = "nova"
    media_output_dir: str = "media_out"
    ffmpeg_path: str | None = None
    tts_provider: str = "openai"
    tts_model: str = "gpt-4o-mini-tts"
    tts_max_chars: int = 3500
    inworld_api_key: str | None = None
    inworld_tts_base_url: str = "https://api.inworld.ai"
    inworld_tts_model: str = "inworld-tts-1.5-max"
    asr_model: str = "whisper-1"
    image_model: str = "gpt-image-1"
    enable_image_generation: bool = False
    image_caption_model: str = "gpt-4o-mini"
    enable_image_caption: bool = False
    enable_tts: bool = False
    enable_asr: bool = False
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    youtube_client_id: str | None = None
    youtube_client_secret: str | None = None
    youtube_token_uri: str = "https://oauth2.googleapis.com/token"
    youtube_privacy_status: str = "public"
    podcast_subscribe_url: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    supabase_url = os.environ.get("SUPABASE_URL", "").strip()
    supabase_key = os.environ.get("SUPABASE_KEY", "").strip()
    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "Missing SUPABASE_URL or SUPABASE_KEY. Set them in the environment."
        )
    tts_provider = os.environ.get("TTS_PROVIDER", "openai")
    tts_max_chars = int(os.environ.get("TTS_MAX_CHARS", "3500"))
    if tts_provider.lower() == "inworld" and tts_max_chars > 2000:
        tts_max_chars = 2000
    return Settings(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        openai_base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        manual_intake_script=os.environ.get("MANUAL_INTAKE_SCRIPT", "scripts/extract_text.py"),
        manual_intake_dir=os.environ.get("MANUAL_INTAKE_DIR"),
        max_words=int(os.environ.get("MAX_WORDS", "2500")),
        request_timeout=int(os.environ.get("REQUEST_TIMEOUT", "30")),
        extraction_max_chars=int(os.environ.get("EXTRACTION_MAX_CHARS", "20000")),
        extraction_use_llm=os.environ.get("EXTRACTION_USE_LLM", "true").lower()
        in ("1", "true", "yes"),
        extraction_model=os.environ.get("EXTRACTION_MODEL", "gpt-5-nano"),
        judge_model=os.environ.get("JUDGE_MODEL", "gpt-4.1-mini"),
        second_judge_model=os.environ.get("SECOND_JUDGE_MODEL", "gpt-4.1-mini"),
        generation_models=[
            m.strip()
            for m in os.environ.get("GENERATION_MODELS", "gpt-4.1-mini").split(",")
            if m.strip()
        ],
        generation_variants=int(os.environ.get("GENERATION_VARIANTS", "3")),
        video_min_score=int(os.environ.get("VIDEO_MIN_SCORE", "6")),
        audio_roundup_model=os.environ.get("AUDIO_ROUNDUP_MODEL", "gpt-5-mini"),
        audio_roundup_size=int(os.environ.get("AUDIO_ROUNDUP_SIZE", "5")),
        audio_roundup_hours=int(os.environ.get("AUDIO_ROUNDUP_HOURS", "24")),
        audio_roundup_voice_a=os.environ.get("AUDIO_ROUNDUP_VOICE_A", "onyx"),
        audio_roundup_voice_b=os.environ.get("AUDIO_ROUNDUP_VOICE_B", "nova"),
        media_output_dir=os.environ.get("MEDIA_OUTPUT_DIR", "media_out"),
        ffmpeg_path=os.environ.get("FFMPEG_PATH"),
        tts_provider=tts_provider,
        tts_model=os.environ.get("TTS_MODEL", "gpt-4o-mini-tts"),
        tts_max_chars=tts_max_chars,
        inworld_api_key=os.environ.get("INWORLD_API_KEY") or os.environ.get("INWORLD_BASE64_KEY"),
        inworld_tts_base_url=os.environ.get("INWORLD_TTS_BASE_URL", "https://api.inworld.ai"),
        inworld_tts_model=os.environ.get("INWORLD_TTS_MODEL", "inworld-tts-1.5-max"),
        asr_model=os.environ.get("ASR_MODEL", "whisper-1"),
        image_model=os.environ.get("IMAGE_MODEL", "gpt-image-1"),
        enable_image_generation=os.environ.get("ENABLE_IMAGE_GENERATION", "false").lower()
        in ("1", "true", "yes"),
        image_caption_model=os.environ.get("IMAGE_CAPTION_MODEL", "gpt-4o-mini"),
        enable_image_caption=os.environ.get("ENABLE_IMAGE_CAPTION", "false").lower()
        in ("1", "true", "yes"),
        enable_tts=os.environ.get("ENABLE_TTS", "false").lower() in ("1", "true", "yes"),
        enable_asr=os.environ.get("ENABLE_ASR", "false").lower() in ("1", "true", "yes"),
        youtube_client_id=os.environ.get("YOUTUBE_CLIENT_ID"),
        youtube_client_secret=os.environ.get("YOUTUBE_CLIENT_SECRET"),
        youtube_token_uri=os.environ.get("YOUTUBE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
        youtube_privacy_status=os.environ.get("YOUTUBE_PRIVACY_STATUS", "public"),
        podcast_subscribe_url=os.environ.get("PODCAST_SUBSCRIBE_URL"),
    )
