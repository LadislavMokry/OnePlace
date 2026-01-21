from app.ai.openai_client import OpenAIClient
from app.config import get_settings


SYSTEM_PROMPT = (
    "You are an image captioning assistant. Describe only what is clearly visible "
    "in 1-3 sentences. Include key subjects, objects, setting, and any readable text "
    "or logos if present. Do not guess identities or events; if something is unclear, "
    "say so explicitly. Avoid speculation."
)


def caption_image(image_url: str) -> str:
    settings = get_settings()
    if not settings.enable_image_caption:
        return ""
    if not image_url:
        return ""
    client = OpenAIClient()
    try:
        return client.chat_text_with_image(
            model=settings.image_caption_model,
            system=SYSTEM_PROMPT,
            user_text="Caption this image for a news roundup.",
            image_url=image_url,
            temperature=0.2,
            max_tokens=200,
            reasoning_effort="minimal",
        ).strip()
    except Exception:
        return ""
