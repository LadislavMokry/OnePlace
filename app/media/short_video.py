import base64
import json
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

import requests
from PIL import Image

from app.ai.asr import transcribe_audio
from app.ai.image import generate_image
from app.ai.tts import generate_voiceover
from app.config import get_settings
from app.media.video import assemble_video, create_placeholder_images


def _chunks(text: str, max_chars: int | None = None) -> Iterable[str]:
    if not text:
        return []
    if max_chars is None:
        max_chars = get_settings().tts_max_chars
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        if end < len(text):
            for sep in [". ", "! ", "? ", "\n"]:
                idx = text.rfind(sep, start, end)
                if idx > start:
                    end = idx + len(sep)
                    break
        yield text[start:end].strip()
        start = end


def _download_image(url: str, path: Path) -> None:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    path.write_bytes(resp.content)


def _write_image_from_b64(data: str, path: Path) -> None:
    path.write_bytes(base64.b64decode(data))


def _resize_to_vertical(path: Path, size: tuple[int, int] = (1080, 1920)) -> None:
    img = Image.open(path)
    img = img.convert("RGB")
    img = img.resize(size, Image.LANCZOS)
    img.save(path)


def _render_voiceover(script: str, output_path: Path, voice: str = "onyx") -> Path:
    settings = get_settings()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = output_path.parent / "tmp_voice"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    parts: list[Path] = []
    idx = 1
    for chunk in _chunks(script):
        part = tmp_dir / f"chunk_{idx:03d}.mp3"
        generate_voiceover(chunk, part, voice=voice)
        parts.append(part)
        idx += 1
    if not parts:
        raise RuntimeError("No voiceover chunks generated")

    ffmpeg_bin = settings.ffmpeg_path or shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg not found. Set FFMPEG_PATH or add ffmpeg to PATH.")

    concat_file = tmp_dir / "concat.txt"
    concat_file.write_text("\n".join([f"file '{p.name}'" for p in parts]))
    cmd = [
        ffmpeg_bin,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        "concat.txt",
        "-c",
        "copy",
        str(output_path.resolve()),
    ]
    subprocess.run(cmd, check=True, cwd=tmp_dir)
    return output_path


def _escape_ass(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def _write_ass_karaoke(words: list[dict], path: Path, max_words: int = 8) -> Path:
    header = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,Arial,64,&H00FFFFFF,&H0000FFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,3,2,2,40,40,80,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    lines = list(header)
    if not words:
        path.write_text("\n".join(lines), encoding="utf-8")
        return path
    idx = 0
    while idx < len(words):
        chunk = words[idx : idx + max_words]
        start = chunk[0]["start"]
        end = chunk[-1]["end"]
        text_parts = []
        for w in chunk:
            dur = max(1, int(round((w["end"] - w["start"]) * 100)))
            text_parts.append(r"{\k" + str(dur) + "}" + _escape_ass(w["word"].strip()))
        line_text = " ".join(text_parts)
        lines.append(
            f"Dialogue: 0,{_format_ass_time(start)},{_format_ass_time(end)},Default,,0,0,0,,{line_text}"
        )
        idx += max_words
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _audio_duration_seconds(audio_path: Path) -> float:
    settings = get_settings()
    ffprobe = settings.ffmpeg_path or shutil.which("ffprobe")
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


def _format_ass_time(seconds: float) -> str:
    total_cs = int(round(seconds * 100))
    h = total_cs // 360000
    m = (total_cs % 360000) // 6000
    s = (total_cs % 6000) // 100
    cs = total_cs % 100
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def render_short_video(content: dict, output_path: Path) -> Path:
    settings = get_settings()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = output_path.parent / "tmp_video"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    scenes = content.get("scenes") or []
    captions = content.get("captions") or []
    script = content.get("script") or ""
    duration_seconds = int(content.get("duration_seconds") or 45)

    scene_texts = [s.get("scene_text") or "" for s in scenes] if scenes else []
    image_prompts = [s.get("image_prompt") or "" for s in scenes] if scenes else []

    images: list[Path] = []
    if settings.enable_image_generation and image_prompts:
        for idx, prompt in enumerate(image_prompts, start=1):
            img_path = tmp_dir / f"scene_{idx:02d}.png"
            try:
                result = generate_image(prompt, size="1024x1536")
                if result.startswith("http"):
                    _download_image(result, img_path)
                else:
                    _write_image_from_b64(result, img_path)
                _resize_to_vertical(img_path)
                images.append(img_path)
            except Exception as exc:
                print(f"image_generation_failed scene={idx} error={exc}")
                images = []
                break

    if not images:
        images = create_placeholder_images(
            scene_texts or [script[:120] or "Scene"] * 8,
            tmp_dir,
        )

    voice_path = tmp_dir / "voiceover.mp3"
    _render_voiceover(script, voice_path, voice=settings.audio_roundup_voice_a)

    captions_path = tmp_dir / "captions.ass"
    normalized: list[dict] = []
    if settings.enable_asr:
        try:
            asr = transcribe_audio(str(voice_path), with_timestamps=True)
            if isinstance(asr, dict):
                words = asr.get("words") or []
                if not words and isinstance(asr.get("segments"), list):
                    for seg in asr.get("segments"):
                        for w in seg.get("words") or []:
                            words.append(w)
                for w in words:
                    if not isinstance(w, dict):
                        continue
                    if "start" in w and "end" in w and "word" in w:
                        normalized.append(w)
        except Exception as exc:
            print(f"asr_failed error={exc}")
            normalized = []

    if not normalized:
        duration = _audio_duration_seconds(voice_path) or float(duration_seconds)
        tokens = (script or "").split()
        if not tokens and captions:
            tokens = " ".join(captions).split()
        if tokens and duration > 0:
            step = duration / max(1, len(tokens))
            t = 0.0
            for token in tokens:
                normalized.append({"word": token, "start": t, "end": t + step})
                t += step

    _write_ass_karaoke(normalized, captions_path)

    seconds_per_image = max(2, int(duration_seconds / max(1, len(images))))
    assemble_video(
        images=images,
        audio_path=voice_path,
        output_path=output_path,
        seconds_per_image=seconds_per_image,
        captions_path=captions_path,
    )
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return output_path
