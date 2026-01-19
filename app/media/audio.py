import itertools
from pathlib import Path
from typing import Iterable
import shutil

from app.ai.tts import generate_voiceover
from app.config import get_settings


def _chunks(text: str, max_chars: int = 3500) -> Iterable[str]:
    if not text:
        return []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        # try to split on sentence boundary
        if end < len(text):
            for sep in [". ", "! ", "? ", "\n"]:
                idx = text.rfind(sep, start, end)
                if idx > start:
                    end = idx + len(sep)
                    break
        yield text[start:end].strip()
        start = end


def render_audio_roundup(dialogue: list[dict], output_path: Path) -> Path:
    settings = get_settings()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_dir = output_path.parent / "tmp_audio"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    audio_parts: list[Path] = []
    counter = itertools.count(1)
    for turn in dialogue:
        speaker = (turn.get("speaker") or "").lower()
        text = (turn.get("text") or "").strip()
        if not text:
            continue
        voice = settings.audio_roundup_voice_a if speaker == "host_a" else settings.audio_roundup_voice_b
        for chunk in _chunks(text):
            part_path = tmp_dir / f"part_{next(counter):03d}.mp3"
            generate_voiceover(chunk, part_path, voice=voice)
            audio_parts.append(part_path)

    if not audio_parts:
        raise RuntimeError("No audio parts generated")

    concat_file = tmp_dir / "concat.txt"
    # Use paths relative to concat file to avoid Windows path escaping issues.
    concat_lines = [f"file '{p.name}'" for p in audio_parts]
    concat_file.write_text("\n".join(concat_lines))

    # Stitch using ffmpeg concat demuxer
    ffmpeg_bin = settings.ffmpeg_path or shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError("ffmpeg not found. Set FFMPEG_PATH or add ffmpeg to PATH.")

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
    import subprocess

    subprocess.run(cmd, check=True, cwd=tmp_dir)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return output_path
