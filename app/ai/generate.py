from app.ai.openai_client import OpenAIClient
from app.config import get_settings

LANGUAGE_LABELS = {
    "en": "English",
    "es": "Spanish",
    "sk": "Slovak",
}


def _language_label(value: str | None) -> str:
    if not value:
        return LANGUAGE_LABELS["en"]
    key = value.strip().lower()
    return LANGUAGE_LABELS.get(key, value.strip())


def _system_prompt(language: str | None, extra_prompt: str | None = None) -> str:
    language_label = _language_label(language)
    base = (
        "You are a short-form video scriptwriter. Return JSON for a single video with keys: "
        "title, hook, script, scenes, captions, duration_seconds. "
        "scenes must be an array of 8-10 items. Each scene item must include: "
        "scene_text, image_prompt, duration_seconds. "
        "captions must be an array of short lines (<= 12 words each) aligned to the script. "
        f"Language: {language_label}. Keep it punchy and current."
    )
    if extra_prompt and extra_prompt.strip():
        return base + "\n\nAdditional instructions: " + extra_prompt.strip()
    return base


def generate_video_variant(
    content: str,
    model: str,
    variant_id: int,
    language: str | None = None,
    extra_prompt: str | None = None,
) -> dict:
    settings = get_settings()
    client = OpenAIClient()
    user = (
        "Article content:\n"
        f"{content}\n\n"
        f"Variant: {variant_id}\n"
        "Return JSON."
    )
    result = client.chat_json(
        model=model,
        system=_system_prompt(language, extra_prompt=extra_prompt),
        user=user,
        temperature=0.7,
        max_tokens=1400,
        reasoning_effort="minimal",
    )
    if isinstance(result, dict):
        result["variant_id"] = variant_id
    return result


def generation_models() -> list[str]:
    settings = get_settings()
    return settings.generation_models
