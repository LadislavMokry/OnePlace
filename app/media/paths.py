from pathlib import Path


def roundup_dir(base_dir: Path, post_id: str) -> Path:
    return base_dir / "roundup" / post_id


def roundup_audio_path(base_dir: Path, post_id: str) -> Path:
    return roundup_dir(base_dir, post_id) / "audio.mp3"


def roundup_video_path(base_dir: Path, post_id: str) -> Path:
    return roundup_dir(base_dir, post_id) / "video.mp4"


def roundup_image_path(base_dir: Path, post_id: str) -> Path:
    return roundup_dir(base_dir, post_id) / "image.png"


def short_video_dir(base_dir: Path, post_id: str) -> Path:
    return base_dir / "short" / post_id


def short_video_path(base_dir: Path, post_id: str) -> Path:
    return short_video_dir(base_dir, post_id) / "video.mp4"
