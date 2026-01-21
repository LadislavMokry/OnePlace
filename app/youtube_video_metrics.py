from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.admin import list_projects
from app.config import get_settings
from app.db import get_supabase

CHECKPOINTS_HOURS: dict[str, int] = {
    "1h": 1,
    "12h": 12,
    "24h": 24,
    "3d": 72,
    "7d": 168,
    "14d": 336,
    "30d": 720,
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


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


def _get_channel_id(creds: Credentials) -> str | None:
    youtube = build("youtube", "v3", credentials=creds)
    resp = youtube.channels().list(part="id", mine=True).execute()
    items = resp.get("items", []) if resp else []
    if not items:
        return None
    return items[0].get("id")


def _parse_video_id(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    if "youtu.be" in parsed.netloc:
        return parsed.path.strip("/").split("/")[0] or None
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query or "")
        vid = qs.get("v", [None])[0]
        if vid:
            return vid
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/")[2] if len(parsed.path.split("/")) > 2 else None
    return None


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _fetch_video_stats(youtube: Any, video_id: str) -> dict:
    resp = youtube.videos().list(part="statistics", id=video_id).execute()
    items = resp.get("items", []) if resp else []
    if not items:
        return {}
    stats = items[0].get("statistics") or {}
    return {
        "views": _to_int(stats.get("viewCount")),
        "likes": _to_int(stats.get("likeCount")),
        "comments": _to_int(stats.get("commentCount")),
    }


def _fetch_analytics_stats(
    analytics: Any,
    channel_id: str,
    video_id: str,
    posted_at: datetime,
    checkpoint_hours: int,
) -> dict:
    start_date = posted_at.date()
    end_dt = posted_at + timedelta(hours=checkpoint_hours)
    yesterday = (_now() - timedelta(days=1)).date()
    end_date = min(end_dt.date(), yesterday)
    if end_date < start_date:
        return {}
    report = (
        analytics.reports()
        .query(
            ids=f"channel=={channel_id}",
            startDate=start_date.isoformat(),
            endDate=end_date.isoformat(),
            metrics="estimatedMinutesWatched,averageViewDuration",
            filters=f"video=={video_id}",
        )
        .execute()
    )
    rows = report.get("rows") or []
    if not rows:
        return {}
    return {
        "watch_time_minutes": _to_float(rows[0][0]),
        "average_view_duration_seconds": _to_float(rows[0][1]),
    }


def _resolve_project_ids(posts: list[dict]) -> dict[str, str | None]:
    sb = get_supabase()
    post_ids = [p["id"] for p in posts if p.get("id")]
    if not post_ids:
        return {}
    usage = (
        sb.table("article_usage")
        .select("post_id, article_id")
        .in_("post_id", post_ids)
        .execute()
        .data
        or []
    )
    article_ids = list({u.get("article_id") for u in usage if u.get("article_id")})
    if not article_ids:
        return {}
    articles = (
        sb.table("articles")
        .select("id, project_id")
        .in_("id", article_ids)
        .execute()
        .data
        or []
    )
    article_project = {a["id"]: a.get("project_id") for a in articles if a.get("id")}
    post_project: dict[str, str | None] = {}
    for row in usage:
        post_id = row.get("post_id")
        article_id = row.get("article_id")
        if post_id and article_id:
            post_project[post_id] = article_project.get(article_id)
    return post_project


def _list_posted_roundups(limit: int = 50) -> list[dict]:
    sb = get_supabase()
    resp = (
        sb.table("posts")
        .select("id, post_url, posted_at, content, created_at")
        .eq("content_type", "audio_roundup")
        .eq("posted", True)
        .order("posted_at", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data or []


def _existing_metrics(post_id: str) -> dict[str, dict]:
    sb = get_supabase()
    resp = (
        sb.table("youtube_video_metrics")
        .select("checkpoint, watch_time_minutes, average_view_duration_seconds")
        .eq("post_id", post_id)
        .execute()
    )
    rows = resp.data or []
    return {row.get("checkpoint"): row for row in rows if row.get("checkpoint")}


def fetch_youtube_video_metrics_for_project(project_id: str, max_posts: int = 50) -> dict:
    account = _get_youtube_account(project_id)
    if not account or not account.get("refresh_token"):
        return {"status": "missing_account"}
    scopes = account.get("scopes") or []
    if "https://www.googleapis.com/auth/youtube.readonly" not in scopes:
        return {"status": "missing_scope"}

    posts = _list_posted_roundups(limit=max_posts)
    if not posts:
        return {"status": "no_posts"}
    post_project = _resolve_project_ids(posts)
    posts = [p for p in posts if post_project.get(p["id"]) == project_id]
    if not posts:
        return {"status": "no_posts"}

    creds = _credentials(account["refresh_token"], scopes)
    youtube = build("youtube", "v3", credentials=creds)
    analytics = build("youtubeAnalytics", "v2", credentials=creds)
    channel_id = _get_channel_id(creds)
    if not channel_id:
        return {"status": "no_channel"}

    sb = get_supabase()
    now = _now()
    inserted = 0
    updated = 0

    for post in posts:
        post_id = post.get("id")
        post_url = post.get("post_url")
        if not post_id or not post_url:
            continue
        video_id = _parse_video_id(post_url)
        if not video_id:
            continue
        posted_at_raw = post.get("posted_at") or post.get("created_at")
        if not posted_at_raw:
            continue
        try:
            posted_at = datetime.fromisoformat(posted_at_raw.replace("Z", "+00:00"))
        except Exception:
            continue
        elapsed_hours = (now - posted_at).total_seconds() / 3600
        existing = _existing_metrics(post_id)

        for checkpoint, hours in CHECKPOINTS_HOURS.items():
            if elapsed_hours < hours:
                continue
            if checkpoint not in existing:
                stats = _fetch_video_stats(youtube, video_id)
                analytics_stats = _fetch_analytics_stats(
                    analytics, channel_id, video_id, posted_at, hours
                )
                payload = {
                    "project_id": project_id,
                    "post_id": post_id,
                    "video_id": video_id,
                    "checkpoint": checkpoint,
                    "views": stats.get("views"),
                    "likes": stats.get("likes"),
                    "comments": stats.get("comments"),
                    "watch_time_minutes": analytics_stats.get("watch_time_minutes"),
                    "average_view_duration_seconds": analytics_stats.get("average_view_duration_seconds"),
                    "collected_at": now.isoformat(),
                    "created_at": now.isoformat(),
                    "updated_at": now.isoformat(),
                }
                sb.table("youtube_video_metrics").insert(payload).execute()
                inserted += 1
                continue
            existing_row = existing.get(checkpoint) or {}
            if (
                existing_row.get("watch_time_minutes") is None
                or existing_row.get("average_view_duration_seconds") is None
            ):
                analytics_stats = _fetch_analytics_stats(
                    analytics, channel_id, video_id, posted_at, hours
                )
                if analytics_stats:
                    sb.table("youtube_video_metrics").update(
                        {
                            "watch_time_minutes": analytics_stats.get("watch_time_minutes"),
                            "average_view_duration_seconds": analytics_stats.get(
                                "average_view_duration_seconds"
                            ),
                            "updated_at": now.isoformat(),
                        }
                    ).eq("post_id", post_id).eq("checkpoint", checkpoint).execute()
                    updated += 1

    return {"status": "ok", "inserted": inserted, "updated": updated}


def fetch_youtube_video_metrics_all(max_posts: int = 50) -> list[dict]:
    results: list[dict] = []
    projects = list_projects()
    for project in projects:
        project_id = project.get("id")
        if not project_id:
            continue
        result = fetch_youtube_video_metrics_for_project(project_id, max_posts=max_posts)
        result["project_id"] = project_id
        result["project_name"] = project.get("name")
        results.append(result)
    return results
