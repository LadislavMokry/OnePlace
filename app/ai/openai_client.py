import json
import time
from typing import Any

import requests

from app.config import get_settings


class OpenAIClient:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self._api_key = settings.openai_api_key
        self._base_url = settings.openai_base_url.rstrip("/")
        self._timeout = settings.request_timeout

    def _supports_temperature(self, model: str) -> bool:
        return not model.startswith("gpt-5")

    def _default_reasoning_effort(self, model: str) -> str | None:
        if model.startswith("gpt-5"):
            return "minimal"
        return None

    def _supports_reasoning_effort(self, model: str) -> bool:
        return model.startswith("gpt-5")

    def _max_tokens_param(self, model: str) -> str:
        return "max_completion_tokens" if model.startswith("gpt-5") else "max_tokens"

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _post(self, path: str, payload: dict, retries: int = 2) -> requests.Response:
        last_err: Exception | None = None
        for attempt in range(retries + 1):
            try:
                return requests.post(
                    f"{self._base_url}{path}",
                    headers=self._headers(),
                    json=payload,
                    timeout=self._timeout,
                )
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as exc:
                last_err = exc
                if attempt >= retries:
                    raise
                time.sleep(1 + attempt)
        raise last_err or RuntimeError("OpenAI request failed")

    def chat_json(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.2,
        max_tokens: int = 800,
        reasoning_effort: str | None = None,
    ) -> dict:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            self._max_tokens_param(model): max_tokens,
            "response_format": {"type": "json_object"},
        }
        if self._supports_temperature(model):
            payload["temperature"] = temperature
        effort = reasoning_effort or self._default_reasoning_effort(model)
        if effort and self._supports_reasoning_effort(model):
            payload["reasoning_effort"] = effort
        resp = self._post("/chat/completions", payload)
        if not resp.ok:
            raise RuntimeError(f"OpenAI error {resp.status_code}: {resp.text}")
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not str(content).strip():
            raise RuntimeError(f"OpenAI returned empty content: {data}")
        return _parse_json(content)

    def chat_text(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.6,
        max_tokens: int = 800,
        reasoning_effort: str | None = None,
    ) -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            self._max_tokens_param(model): max_tokens,
        }
        if self._supports_temperature(model):
            payload["temperature"] = temperature
        effort = reasoning_effort or self._default_reasoning_effort(model)
        if effort and self._supports_reasoning_effort(model):
            payload["reasoning_effort"] = effort
        resp = self._post("/chat/completions", payload)
        if not resp.ok:
            raise RuntimeError(f"OpenAI error {resp.status_code}: {resp.text}")
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not str(content).strip():
            raise RuntimeError(f"OpenAI returned empty content: {data}")
        return content

    def chat_text_with_image(
        self,
        model: str,
        system: str,
        user_text: str,
        image_url: str,
        temperature: float = 0.4,
        max_tokens: int = 300,
        reasoning_effort: str | None = None,
    ) -> str:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
            self._max_tokens_param(model): max_tokens,
        }
        if self._supports_temperature(model):
            payload["temperature"] = temperature
        effort = reasoning_effort or self._default_reasoning_effort(model)
        if effort and self._supports_reasoning_effort(model):
            payload["reasoning_effort"] = effort
        resp = self._post("/chat/completions", payload)
        if not resp.ok:
            raise RuntimeError(f"OpenAI error {resp.status_code}: {resp.text}")
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not str(content).strip():
            raise RuntimeError(f"OpenAI returned empty content: {data}")
        return content

    def tts(self, model: str, voice: str, text: str) -> bytes:
        payload = {"model": model, "voice": voice, "input": text}
        resp = self._post("/audio/speech", payload)
        resp.raise_for_status()
        return resp.content

    def asr(
        self,
        model: str,
        audio_path: str,
        response_format: str = "text",
        timestamp_granularities: list[str] | None = None,
    ):
        with open(audio_path, "rb") as f:
            resp = requests.post(
                f"{self._base_url}/audio/transcriptions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                files={"file": f},
                data={
                    "model": model,
                    "response_format": response_format,
                    "timestamp_granularities": timestamp_granularities or [],
                },
                timeout=self._timeout,
            )
        resp.raise_for_status()
        if response_format == "text":
            return resp.text
        return resp.json()

    def image(self, model: str, prompt: str, size: str = "1024x1024", quality: str = "low") -> str:
        payload = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "quality": quality,
        }
        # DALL·E models can return URLs or base64; GPT image models always return base64.
        if model.startswith("dall-e"):
            payload["response_format"] = "b64_json"
        # Image API uses /images/generations for text-to-image.
        resp = self._post("/images/generations", payload)
        resp.raise_for_status()
        data = resp.json()
        # Expecting base64 or URL depending on API. Prefer URL if present.
        if "data" in data and data["data"]:
            return data["data"][0].get("url") or data["data"][0].get("b64_json", "")
        return ""


def _parse_json(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback: try to extract JSON object from text
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(content[start : end + 1])
        raise
