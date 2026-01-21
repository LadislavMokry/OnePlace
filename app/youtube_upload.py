import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from app.admin import list_projects
from app.config import get_settings
from app.db import get_supabase
from app.media.paths import roundup_audio_path, roundup_image_path, roundup_video_path
from app.media.roundup_video import ensure_roundup_image, render_audio_roundup_video
from app.pipeline import fetch_latest_audio_roundup_for_project


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_client_secrets(settings: Any) -> tuple[str, str]:
    if settings.youtube_client_id and settings.youtube_client_secret:
        return settings.youtube_client_id, settings.youtube_client_secret
    creds_path = Path(__file__).resolve().parent.parent / "credentials.json"
    if not creds_path.exists():
        raise RuntimeError("Missing YouTube client credentials. Set YOUTUBE_CLIENT_ID/SECRET or credentials.json.")
    data = json.loads(creds_path.read_text(encoding="utf-8"))
    block = data.get("installed") or data.get("web") or {}
    client_id = block.get("client_id")
    client_secret = block.get("client_secret")
    if not client_id or not client_secret:
        raise RuntimeError("Invalid credentials.json: missing client_id/client_secret.")
    return client_id, client_secret


def _credentials(refresh_token: str, scopes: list[str]) -> Credentials:
    settings = get_settings()
    client_id, client_secret = _load_client_secrets(settings)
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=settings.youtube_token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes or None,
    )
    creds.refresh(Request())
    return creds


def _project_language(project_id: str) -> str | None:
    sb = get_supabase()
    resp = (
        sb.table("projects")
        .select("language")
        .eq("id", project_id)
        .limit(1)
        .execute()
    )
    data = resp.data or []
    return data[0].get("language") if data else None


def _project_name(project_id: str) -> str:
    sb = get_supabase()
    resp = (
        sb.table("projects")
        .select("name")
        .eq("id", project_id)
        .limit(1)
        .execute()
    )
    data = resp.data or []
    return data[0].get("name") or "Daily Roundup" if data else "Daily Roundup"


def _normalize_tags(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return []


def _default_title(project_name: str, language: str | None) -> str:
    date_str = datetime.now(timezone.utc).strftime("%b %d, %Y")
    if language and language.lower().startswith("es"):
        return f"{project_name} — Resumen diario ({date_str})"
    if language and language.lower().startswith("sk"):
        return f"{project_name} — Denný prehľad ({date_str})"
    return f"{project_name} — Daily Roundup ({date_str})"


def _default_description(project_name: str, language: str | None, subscribe_url: str | None) -> str:
    if language and language.lower().startswith("es"):
        base = f"{project_name}: episodio diario de 7–10 minutos."
        cta = "Escucha el podcast completo en nuestra suscripción."
    elif language and language.lower().startswith("sk"):
        base = f"{project_name}: denný 7–10 minútový podcast."
        cta = "Celú epizódu nájdeš v našom predplatnom."
    else:
        base = f"{project_name}: 7–10 minute daily podcast."
        cta = "Listen to the full episode on our subscriber feed."
    if subscribe_url:
        return f"{base}\n\n{cta}\n{subscribe_url}"
    return f"{base}\n\n{cta}"


def _ensure_roundup_assets(post: dict) -> tuple[Path, Path, dict]:
    settings = get_settings()
    content = post.get("content") or {}
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            content = {}

    out_dir = Path(settings.media_output_dir)
    video_path = roundup_video_path(out_dir, post["id"])
    if not video_path.exists():
        render_audio_roundup_video(content, post["id"], video_path)
    image_path = roundup_image_path(out_dir, post["id"])
    if not image_path.exists():
        prompt = content.get("image_prompt") or content.get("imagePrompt")
        ensure_roundup_image(prompt, image_path, allow_placeholder=True)
    return video_path, image_path, content


def _get_youtube_account(project_id: str) -> dict | None:
    sb = get_supabase()
    resp = (
        sb.table("youtube_accounts")
        .select("*")
        .eq("project_id", project_id)
        .limit(1)
        .execute()
    )
    data = resp.data or []
    return data[0] if data else None


def _mark_post_uploaded(post_id: str, video_url: str) -> None:
    sb = get_supabase()
    sb.table("posts").update(
        {
            "posted": True,
            "posted_at": _now_iso(),
            "post_url": video_url,
            "media_urls": [video_url],
        }
    ).eq("id", post_id).execute()


def _record_audio_run(
    project_id: str,
    post_id: str,
    content: dict,
    status: str = "ok",
    error: str | None = None,
) -> None:
    settings = get_settings()
    audio_url = f"/api/audio-roundup/{post_id}/audio"
    voices = f"host_a:{settings.audio_roundup_voice_a},host_b:{settings.audio_roundup_voice_b}"
    payload = {
        "project_id": project_id,
        "post_id": post_id,
        "content_type": "audio_roundup",
        "script_provider": "openai",
        "script_model": settings.audio_roundup_model,
        "tts_provider": "openai",
        "tts_model": settings.tts_model,
        "tts_voice": voices,
        "audio_url": audio_url,
        "duration_seconds": int(content.get("duration_seconds") or 0) or None,
        "status": status,
        "error": error,
        "created_at": _now_iso(),
    }
    sb = get_supabase()
    sb.table("audio_generation_runs").insert(payload).execute()


def upload_latest_roundup_for_project(project_id: str) -> dict:
    account = _get_youtube_account(project_id)
    if not account or not account.get("refresh_token"):
        return {"status": "missing_account"}

    post = fetch_latest_audio_roundup_for_project(project_id)
    if not post:
        return {"status": "no_roundup"}

    if post.get("posted"):
        return {"status": "already_posted", "post_id": post.get("id")}

    settings = get_settings()
    scopes = account.get("scopes") or [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.readonly",
    ]
    creds = _credentials(account["refresh_token"], scopes)
    youtube = build("youtube", "v3", credentials=creds)

    video_path, image_path, content = _ensure_roundup_assets(post)
    language = _project_language(project_id) or "en"
    project_name = _project_name(project_id)

    title = content.get("title") or content.get("youtube_title") or _default_title(project_name, language)
    description = content.get("description") or content.get("youtube_description") or _default_description(
        project_name, language, settings.podcast_subscribe_url
    )
    tags = _normalize_tags(content.get("tags") or content.get("youtube_tags") or [])

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "24",
            "defaultLanguage": language,
            "defaultAudioLanguage": language,
        },
        "status": {
            "privacyStatus": settings.youtube_privacy_status,
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
            "license": "youtube",
        },
    }

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True),
    )
    response = request.execute()
    video_id = response.get("id")
    if not video_id:
        _record_audio_run(project_id, post["id"], content, status="error", error="missing_video_id")
        return {"status": "error", "error": "missing_video_id"}

    if image_path.exists():
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(image_path), mimetype="image/png"),
        ).execute()

    video_url = f"https://youtu.be/{video_id}"
    _mark_post_uploaded(post["id"], video_url)
    _record_audio_run(project_id, post["id"], content, status="ok")
    return {"status": "ok", "video_id": video_id, "url": video_url}


def upload_latest_roundups_all() -> list[dict]:
    results: list[dict] = []
    projects = list_projects()
    for project in projects:
        project_id = project.get("id")
        if not project_id:
            continue
        result = upload_latest_roundup_for_project(project_id)
        result["project_id"] = project_id
        result["project_name"] = project.get("name")
        results.append(result)
    return results
