import base64
import shutil
import subprocess
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageOps

from app.ai.image import generate_image
from app.config import get_settings
from app.media.audio import render_audio_roundup
from app.media.video import assemble_video
from app.media.paths import podcast_image_path


def _download_image(url: str, path: Path) -> None:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    path.write_bytes(resp.content)


def _write_image_from_b64(data: str, path: Path) -> None:
    path.write_bytes(base64.b64decode(data))


def _resize_to_landscape(path: Path, size: tuple[int, int] = (1280, 720)) -> None:
    img = Image.open(path)
    img = img.convert("RGB")
    img = ImageOps.fit(img, size, Image.LANCZOS)
    img.save(path)

def _resize_to_square(path: Path, size: tuple[int, int] = (1024, 1024)) -> None:
    img = Image.open(path)
    img = img.convert("RGB")
    img = ImageOps.fit(img, size, Image.LANCZOS)
    img.save(path)


def _create_placeholder(path: Path, text: str = "Audio Roundup") -> None:
    img = Image.new("RGB", (1280, 720), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)
    caption = (text or "Audio Roundup")[:120]
    draw.text((60, 80), caption, fill=(255, 255, 255))
    img.save(path)


def _audio_duration_seconds(audio_path: Path) -> float:
    settings = get_settings()
    ffprobe = shutil.which("ffprobe")
    if settings.ffmpeg_path:
        base = Path(settings.ffmpeg_path).parent
        candidate = base / "ffprobe.exe"
        if candidate.exists():
            ffprobe = str(candidate)
    if not ffprobe:
        return 0.0
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]
    try:
        out = subprocess.check_output(cmd, text=True).strip()
        return float(out) if out else 0.0
    except Exception:
        return 0.0


def ensure_roundup_image(prompt: str | None, output_path: Path, allow_placeholder: bool = False) -> Path | None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        return output_path
    settings = get_settings()
    prompt_text = (prompt or "").strip()
    if prompt_text and settings.enable_image_generation:
        try:
            result = generate_image(prompt_text, size="1536x1024", quality="low")
            if result.startswith("http"):
                _download_image(result, output_path)
            else:
                _write_image_from_b64(result, output_path)
            _resize_to_landscape(output_path)
            return output_path
        except Exception as exc:
            print(f"roundup_image_failed error={exc}")
    if not allow_placeholder:
        return None
    _create_placeholder(output_path, prompt_text or "Audio Roundup")
    return output_path


def ensure_project_podcast_image(
    prompt: str | None, output_path: Path, allow_placeholder: bool = False
) -> Path | None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        return output_path
    settings = get_settings()
    prompt_text = (prompt or "").strip()
    if prompt_text and settings.enable_image_generation:
        try:
            result = generate_image(prompt_text, size="1024x1024", quality="low")
            if result.startswith("http"):
                _download_image(result, output_path)
            else:
                _write_image_from_b64(result, output_path)
            _resize_to_square(output_path)
            return output_path
        except Exception as exc:
            print(f"project_image_failed error={exc}")
    if not allow_placeholder:
        return None
    _create_placeholder(output_path, prompt_text or "Podcast")
    return output_path


def render_audio_roundup_video(
    content: dict,
    post_id: str,
    output_path: Path,
    project_id: str | None = None,
    project_prompt: str | None = None,
) -> Path:
    settings = get_settings()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio_path = output_path.parent / "audio.mp3"
    if not audio_path.exists():
        dialogue = content.get("dialogue") or []
        voice_a = content.get("tts_voice_a")
        voice_b = content.get("tts_voice_b")
        render_audio_roundup(dialogue, audio_path, voice_a=voice_a, voice_b=voice_b)

    image = None
    if project_id and project_prompt:
        base_dir = Path(settings.media_output_dir)
        image = ensure_project_podcast_image(
            project_prompt, podcast_image_path(base_dir, project_id), allow_placeholder=True
        )
    if not image:
        image_path = output_path.parent / "image.png"
        prompt = content.get("image_prompt") or content.get("imagePrompt")
        image = ensure_roundup_image(prompt, image_path, allow_placeholder=True)
    if not image:
        raise RuntimeError("Unable to generate or create a roundup image")

    duration = _audio_duration_seconds(audio_path)
    if not duration:
        duration = float(content.get("duration_seconds") or 0) or 60.0
    seconds_per_image = max(2, int(round(duration)))
    assemble_video(
        images=[image],
        audio_path=audio_path,
        output_path=output_path,
        seconds_per_image=seconds_per_image,
    )
    return output_path
