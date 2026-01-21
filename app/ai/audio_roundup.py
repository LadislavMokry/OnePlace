from app.ai.openai_client import OpenAIClient
from app.config import get_settings

LANGUAGE_LABELS = {
    "en": "English",
    "es": "Spanish",
    "sk": "Slovak",
}
MAX_CONTENT_CHARS = 8000
FALLBACK_CONTENT_CHARS = [8000, 4000, 2000]


def _language_label(value: str | None) -> str:
    if not value:
        return LANGUAGE_LABELS["en"]
    key = value.strip().lower()
    return LANGUAGE_LABELS.get(key, value.strip())


def _system_prompt(language: str | None) -> str:
    language_label = _language_label(language)
    return (
        f"You are a podcast writer. Write the script in {language_label}. "
        "Create a 5-7 minute audio roundup script for two hosts "
        "(host_a male, host_b female). You will receive items with title, "
        "summary, and full content. Use the full content when available "
        "(content may be truncated to fit limits). "
        "Structure: open with a fast, punchy teaser rundown of ALL stories "
        "(one sentence each) to hook the listener, then cover each story in "
        "detail one by one. Keep the rundown short and clearly separate it "
        "from the deep dives. "
        "Return JSON with keys: title, description, tags, dialogue "
        "(array of {speaker, text}), duration_seconds, and image_prompt. "
        "title should be short and YouTube-ready. description should be 2-4 "
        "sentences with a clear call-to-action to listen to the full daily podcast. "
        "tags should be an array of 6-12 keywords. "
        "The image_prompt should be a single, vivid sentence for a static "
        "podcast thumbnail background (no text or logos). Keep it concise, "
        "current, and engaging."
    )


def _trim(text: str, max_chars: int) -> str:
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def generate_audio_roundup(items: list[dict], language: str | None = None) -> dict:
    settings = get_settings()
    client = OpenAIClient()
    last_err: Exception | None = None
    for max_chars in FALLBACK_CONTENT_CHARS:
        stories = []
        for item in items:
            summary = (item.get("summary") or "").strip()
            content = (item.get("content") or "").strip()
            if content:
                content = _trim(content, max_chars)
            else:
                content = summary
            stories.append(
                {
                    "title": item.get("title"),
                    "summary": summary,
                    "content": content,
                }
            )
        user = {
            "stories": stories,
            "length_minutes": "5-7",
            "hosts": ["host_a", "host_b"],
            "structure": "teaser_rundown_then_deep_dive",
            "use_all_stories": True,
        }
        try:
            return client.chat_json(
                model=settings.audio_roundup_model,
                system=_system_prompt(language),
                user=f"{user}\nReturn JSON.",
                temperature=0.6,
                max_tokens=3000,
                reasoning_effort="minimal",
            )
        except RuntimeError as exc:
            last_err = exc
            message = str(exc)
            if "empty content" in message or "JSON" in message:
                continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError("Failed to generate audio roundup")
