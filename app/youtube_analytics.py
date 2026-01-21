from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.admin import list_projects
from app.config import get_settings
from app.db import get_supabase


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


def _get_channel_info(creds: Credentials) -> tuple[str | None, str | None]:
    youtube = build("youtube", "v3", credentials=creds)
    resp = youtube.channels().list(part="id,snippet", mine=True).execute()
    items = resp.get("items", []) if resp else []
    if not items:
        return None, None
    channel_id = items[0].get("id")
    channel_title = items[0].get("snippet", {}).get("title")
    return channel_id, channel_title


def _to_int(value: Any) -> int:
    try:
        return int(float(value))
    except Exception:
        return 0


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def fetch_youtube_analytics_for_project(project_id: str, days: int = 7) -> dict:
    account = _get_youtube_account(project_id)
    if not account or not account.get("refresh_token"):
        return {"status": "missing_account"}

    scopes = account.get("scopes") or []
    if "https://www.googleapis.com/auth/yt-analytics.readonly" not in scopes:
        return {"status": "missing_scope"}

    creds = _credentials(account["refresh_token"], scopes)
    channel_id, channel_title = _get_channel_info(creds)
    if not channel_id:
        return {"status": "no_channel"}

    analytics = build("youtubeAnalytics", "v2", credentials=creds)
    end_date = datetime.now(timezone.utc).date() - timedelta(days=1)
    start_date = end_date - timedelta(days=max(days, 1) - 1)
    report = (
        analytics.reports()
        .query(
            ids=f"channel=={channel_id}",
            startDate=start_date.isoformat(),
            endDate=end_date.isoformat(),
            metrics="views,estimatedMinutesWatched,averageViewDuration,likes,comments,subscribersGained",
            dimensions="day",
            sort="day",
        )
        .execute()
    )

    rows = report.get("rows") or []
    if not rows:
        return {"status": "no_data", "channel_id": channel_id, "channel_title": channel_title}

    payloads: list[dict] = []
    now = _now_iso()
    for row in rows:
        if not row:
            continue
        payloads.append(
            {
                "project_id": project_id,
                "channel_id": channel_id,
                "channel_title": channel_title,
                "report_date": row[0],
                "views": _to_int(row[1]),
                "watch_time_minutes": _to_float(row[2]),
                "average_view_duration_seconds": _to_float(row[3]),
                "likes": _to_int(row[4]),
                "comments": _to_int(row[5]),
                "subscribers_gained": _to_int(row[6]),
                "created_at": now,
                "updated_at": now,
            }
        )

    sb = get_supabase()
    sb.table("youtube_metrics").upsert(payloads, on_conflict="project_id,report_date").execute()
    if channel_title:
        sb.table("youtube_accounts").update(
            {"channel_title": channel_title, "updated_at": now}
        ).eq("project_id", project_id).execute()
    return {"status": "ok", "rows": len(payloads), "channel_id": channel_id, "channel_title": channel_title}


def fetch_youtube_analytics_all(days: int = 7) -> list[dict]:
    results: list[dict] = []
    projects = list_projects()
    for project in projects:
        project_id = project.get("id")
        if not project_id:
            continue
        result = fetch_youtube_analytics_for_project(project_id, days=days)
        result["project_id"] = project_id
        result["project_name"] = project.get("name")
        results.append(result)
    return results
