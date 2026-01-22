from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse, parse_qsl, urlsplit, urlunsplit
import hashlib
import re

import feedparser
import requests
import trafilatura

from .ai.image_caption import caption_image
from .config import get_settings
from .db import get_supabase

MAX_CONTENT_CHARS = 4000


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_iso(value: Any) -> str | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
        except Exception:
            return None
    try:
        return datetime.fromtimestamp(calendar.timegm(value), tz=timezone.utc).isoformat()
    except Exception:
        return None


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def _should_scrape_source(source: dict) -> bool:
    interval = int(source.get("scrape_interval_hours") or 6)
    last = _parse_iso(source.get("last_scraped_at"))
    if not last:
        return True
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    age_seconds = (datetime.now(timezone.utc) - last).total_seconds()
    return age_seconds >= interval * 3600


def _truncate(value: str, max_chars: int = MAX_CONTENT_CHARS) -> str:
    if not value:
        return ""
    if len(value) <= max_chars:
        return value
    return value[:max_chars].rsplit(" ", 1)[0]


def _content_hash(text: str) -> str | None:
    if not text:
        return None
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    if not normalized:
        return None
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _looks_like_media(url: str) -> bool:
    if not url:
        return False
    path = urlparse(url).path.lower()
    return path.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mov", ".webm"))


def _request_kwargs(settings: Any, config: dict | None, accept: str | None = None) -> dict:
    headers = {"User-Agent": settings.user_agent}
    if accept:
        headers["Accept"] = accept
    auth = None
    if config and config.get("auth_required"):
        auth_type = (config.get("auth_type") or "none").lower()
        if auth_type == "basic":
            username = config.get("auth_username")
            password = config.get("auth_password")
            if username and password:
                auth = (username, password)
        elif auth_type == "cookie":
            cookie = config.get("auth_cookie")
            if cookie:
                headers["Cookie"] = cookie
        elif auth_type == "header":
            name = config.get("auth_header_name")
            value = config.get("auth_header_value")
            if name and value:
                headers[name] = value
    return {"headers": headers, "timeout": settings.request_timeout, "auth": auth}


def _detect_login_required(
    html: str | None,
    extracted: str | None,
    status_code: int | None,
    url: str | None = None,
) -> str | None:
    if status_code in {401, 403}:
        return f"http_{status_code}"
    if not html:
        return None
    text = (extracted or "").strip()
    lower = html.lower()
    hard_phrases = [
        "sign in to continue",
        "log in to continue",
        "subscribe to continue",
        "subscribe to read",
        "already a subscriber",
        "register to continue",
        "create an account to read",
        "member only",
    ]
    if any(p in lower for p in hard_phrases):
        return "login_wall"
    if len(text) >= 400:
        # Skip generic keyword checks, but still allow site-specific logic below.
        pass
    keywords = [
        "log in",
        "login",
        "sign in",
        "signin",
        "subscribe",
        "subscription",
        "paywall",
        "register",
        "create account",
        "sign up",
        "member only",
        "subscriber",
    ]
    if len(text) < 400 and any(k in lower for k in keywords):
        return "login_wall"
    if url and "formula1.com" in urlparse(url).netloc.lower():
        if ("account.formula1.com" in lower or "subscribe-to-f1-tv" in lower) and (
            "sign in" in lower or "/en/login" in lower or "loginurl" in lower
        ):
            return "login_wall"
    return None


def _mark_auth_required(sb: Any, source_id: str | None, config: dict | None, reason: str) -> None:
    if not source_id:
        return
    payload = dict(config or {})
    payload["auth_required"] = True
    payload["auth_detected_at"] = _now_iso()
    payload["auth_reason"] = reason
    payload["auth_last_check_status"] = "login_required"
    payload["auth_last_check_reason"] = reason
    payload["auth_last_check_at"] = _now_iso()
    sb.table("sources").update({"config": payload, "updated_at": _now_iso()}).eq("id", source_id).execute()


def _mark_auth_checked(sb: Any, source_id: str | None, config: dict | None, status: str, reason: str | None = None) -> None:
    if not source_id:
        return
    payload = dict(config or {})
    payload["auth_last_check_status"] = status
    payload["auth_last_check_reason"] = reason
    payload["auth_last_check_at"] = _now_iso()
    if status == "ok" and not payload.get("auth_required"):
        payload.setdefault("auth_required", False)
    sb.table("sources").update({"config": payload, "updated_at": _now_iso()}).eq("id", source_id).execute()


def _normalize_reddit_listing_url(url: str, max_items: int) -> str:
    if not url:
        return url
    parsed = urlparse(url)
    if "reddit.com" not in parsed.netloc:
        return url
    if parsed.path.endswith(".json") or parsed.path.endswith(".json/"):
        query = parse_qs(parsed.query)
        query.setdefault("limit", [str(max_items)])
        query.setdefault("raw_json", ["1"])
        query_str = urlencode({k: v[0] for k, v in query.items()})
        return urlunparse(parsed._replace(query=query_str))

    path_parts = [p for p in parsed.path.split("/") if p]
    subreddit = None
    if "r" in path_parts:
        idx = path_parts.index("r")
        if idx + 1 < len(path_parts):
            subreddit = path_parts[idx + 1]
    if not subreddit and path_parts:
        if path_parts[0].startswith("r"):
            subreddit = path_parts[0].replace("r", "", 1)
    if not subreddit:
        return url
    sort = next((p for p in path_parts if p in {"top", "new", "hot", "rising"}), "top")
    query = parse_qs(parsed.query)
    timeframe = query.get("t", [None])[0] or "day"
    listing = f"https://www.reddit.com/r/{subreddit}/{sort}/.json"
    params = {"limit": str(max_items), "t": timeframe, "raw_json": "1"}
    return f"{listing}?{urlencode(params)}"


def _extract_reddit_image_url(post: dict) -> str | None:
    if post.get("post_hint") == "image" and post.get("url"):
        return post.get("url")
    preview = post.get("preview") or {}
    images = preview.get("images") or []
    if images:
        source = images[0].get("source") or {}
        url = source.get("url")
        if url:
            return unescape(url)
    return None


def _fetch_article_text(
    url: str,
    settings: Any,
    config: dict | None = None,
    source_id: str | None = None,
    sb: Any | None = None,
) -> str:
    if not url or _looks_like_media(url):
        return ""
    if "reddit.com" in urlparse(url).netloc:
        return ""
    try:
        kwargs = _request_kwargs(settings, config, accept="text/html")
        resp = requests.get(url, **kwargs)
        if resp.status_code in {401, 403}:
            if sb is not None:
                _mark_auth_required(sb, source_id, config, f"http_{resp.status_code}")
            return ""
        resp.raise_for_status()
        extracted = trafilatura.extract(resp.text) or ""
        reason = _detect_login_required(resp.text, extracted, resp.status_code, url=url)
        if reason and sb is not None:
            _mark_auth_required(sb, source_id, config, reason)
        return extracted
    except Exception:
        return ""


def list_projects() -> list[dict]:
    sb = get_supabase()
    res = sb.table("projects").select("*").order("created_at", desc=True).execute()
    return res.data or []


def create_project(
    name: str,
    description: str | None = None,
    language: str | None = None,
    generation_interval_hours: int | None = None,
    unusable_score_threshold: int | None = None,
    unusable_age_hours: int | None = None,
    video_prompt_extra: str | None = None,
    audio_roundup_prompt_extra: str | None = None,
) -> dict:
    sb = get_supabase()
    row = {
        "name": name.strip(),
        "description": description,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    if language and language.strip():
        row["language"] = language.strip()
    if generation_interval_hours is not None:
        row["generation_interval_hours"] = generation_interval_hours
    if unusable_score_threshold is not None:
        row["unusable_score_threshold"] = unusable_score_threshold
    if unusable_age_hours is not None:
        row["unusable_age_hours"] = unusable_age_hours
    if video_prompt_extra and video_prompt_extra.strip():
        row["video_prompt_extra"] = video_prompt_extra.strip()
    if audio_roundup_prompt_extra and audio_roundup_prompt_extra.strip():
        row["audio_roundup_prompt_extra"] = audio_roundup_prompt_extra.strip()
    res = sb.table("projects").insert(row).execute()
    return (res.data or [row])[0]


def update_project(project_id: str, fields: dict) -> dict:
    sb = get_supabase()
    payload = {k: v for k, v in fields.items() if v is not None}
    if "language" in payload and payload["language"]:
        payload["language"] = payload["language"].strip()
    if "video_prompt_extra" in payload and payload["video_prompt_extra"] is not None:
        cleaned = str(payload["video_prompt_extra"]).strip()
        payload["video_prompt_extra"] = cleaned or None
    if "audio_roundup_prompt_extra" in payload and payload["audio_roundup_prompt_extra"] is not None:
        cleaned = str(payload["audio_roundup_prompt_extra"]).strip()
        payload["audio_roundup_prompt_extra"] = cleaned or None
    payload["updated_at"] = _now_iso()
    res = sb.table("projects").update(payload).eq("id", project_id).execute()
    return (res.data or [payload])[0]


def delete_project(project_id: str) -> None:
    sb = get_supabase()
    sb.table("projects").delete().eq("id", project_id).execute()


def list_sources(project_id: str) -> list[dict]:
    sb = get_supabase()
    res = (
        sb.table("sources")
        .select("*")
        .eq("project_id", project_id)
        .order("created_at", desc=False)
        .execute()
    )
    return res.data or []


def get_source(source_id: str) -> dict | None:
    sb = get_supabase()
    res = sb.table("sources").select("*").eq("id", source_id).limit(1).execute()
    return (res.data or [None])[0]


def create_source(project_id: str, row: dict) -> dict:
    sb = get_supabase()
    payload = {
        "project_id": project_id,
        "name": row["name"].strip(),
        "source_type": row["source_type"].strip().lower(),
        "url": row["url"].strip(),
        "enabled": row.get("enabled", True),
        "config": row.get("config") or {},
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    if row.get("scrape_interval_hours") is not None:
        payload["scrape_interval_hours"] = row.get("scrape_interval_hours")
    res = sb.table("sources").insert(payload).execute()
    return (res.data or [payload])[0]


def update_source(source_id: str, fields: dict) -> dict:
    sb = get_supabase()
    payload = {k: v for k, v in fields.items() if v is not None}
    if "source_type" in payload and payload["source_type"]:
        payload["source_type"] = payload["source_type"].strip().lower()
    if "name" in payload and payload["name"]:
        payload["name"] = payload["name"].strip()
    if "url" in payload and payload["url"]:
        payload["url"] = payload["url"].strip()
    payload["updated_at"] = _now_iso()
    res = sb.table("sources").update(payload).eq("id", source_id).execute()
    return (res.data or [payload])[0]


def delete_source(source_id: str) -> None:
    sb = get_supabase()
    sb.table("sources").delete().eq("id", source_id).execute()


def list_source_items(source_id: str, limit: int = 10) -> list[dict]:
    sb = get_supabase()
    res = (
        sb.table("source_items")
        .select("*")
        .eq("source_id", source_id)
        .order("scraped_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []


def list_articles_page(
    project_id: str,
    limit: int = 50,
    offset: int = 0,
    order_by: str = "score",
    direction: str = "desc",
) -> dict:
    sb = get_supabase()
    query = (
        sb.table("articles")
        .select(
            "id, title, judge_score, scraped_at, processed, scored, unusable, unusable_reason, duplicate_of",
            count="exact",
        )
        .eq("project_id", project_id)
    )
    order_by = (order_by or "score").lower()
    direction = (direction or "desc").lower()
    desc = direction != "asc"
    if order_by == "age":
        query = query.order("scraped_at", desc=desc)
    elif order_by == "status":
        query = (
            query.order("unusable", desc=False)
            .order("scored", desc=True)
            .order("processed", desc=True)
            .order("scraped_at", desc=True)
        )
    else:
        query = query.order("judge_score", desc=desc, nullsfirst=False).order("scraped_at", desc=True)
    query = query.range(offset, offset + limit - 1)
    resp = query.execute()
    items = resp.data or []
    total = resp.count or 0
    if not items:
        return {"items": [], "total": total}
    article_ids = [i["id"] for i in items]
    usage = (
        sb.table("article_usage")
        .select("article_id")
        .in_("article_id", article_ids)
        .eq("usage_type", "audio_roundup")
        .execute()
        .data
        or []
    )
    used_ids = {u["article_id"] for u in usage if u.get("article_id")}
    for item in items:
        item["used_in_audio"] = item["id"] in used_ids
    return {"items": items, "total": total}


def _chunked(values: list[str], size: int = 200) -> list[list[str]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def project_stats(project_id: str) -> dict:
    sb = get_supabase()
    sources = list_sources(project_id)
    stats = []
    for source in sources:
        source_id = source.get("id")
        total = (
            sb.table("articles")
            .select("id", count="exact")
            .eq("project_id", project_id)
            .eq("source_id", source_id)
            .execute()
            .count
            or 0
        )
        used = 0
        avg_score = None
        if total:
            score_sum = 0
            score_count = 0
            offset = 0
            page_size = 1000
            ids = []
            while True:
                page = (
                    sb.table("articles")
                    .select("id, judge_score")
                    .eq("project_id", project_id)
                    .eq("source_id", source_id)
                    .range(offset, offset + page_size - 1)
                    .execute()
                    .data
                    or []
                )
                if not page:
                    break
                for row in page:
                    if row.get("id"):
                        ids.append(row["id"])
                    if row.get("judge_score") is not None:
                        score_sum += row["judge_score"]
                        score_count += 1
                offset += page_size
                if len(page) < page_size:
                    break
            if score_count:
                avg_score = round(score_sum / score_count, 2)
            if ids:
                for chunk in _chunked(ids, size=200):
                    used += (
                        sb.table("article_usage")
                        .select("id", count="exact")
                        .in_("article_id", chunk)
                        .eq("usage_type", "audio_roundup")
                        .execute()
                        .count
                        or 0
                    )
        hitrate = round((used / total) * 100, 1) if total else 0.0
        stats.append(
            {
                "source_id": source_id,
                "source_name": source.get("name"),
                "total_articles": total,
                "used_in_audio": used,
                "hitrate": hitrate,
                "avg_score": avg_score,
                "last_scraped_at": source.get("last_scraped_at"),
            }
        )
    stats.sort(key=lambda x: (x["hitrate"], x["total_articles"]), reverse=True)
    youtube_metrics = project_youtube_metrics(project_id)
    youtube_video_metrics = project_youtube_video_metrics(project_id)
    account = get_youtube_account(project_id)
    return {
        "project_id": project_id,
        "sources": stats,
        "youtube_metrics": youtube_metrics,
        "youtube_video_metrics": youtube_video_metrics,
        "youtube_channel_title": account.get("channel_title") if account else None,
    }


def project_youtube_metrics(project_id: str, days: int = 7) -> list[dict]:
    sb = get_supabase()
    resp = (
        sb.table("youtube_metrics")
        .select(
            "report_date, views, watch_time_minutes, average_view_duration_seconds, "
            "likes, comments, subscribers_gained"
        )
        .eq("project_id", project_id)
        .order("report_date", desc=True)
        .limit(days)
        .execute()
    )
    return resp.data or []


def _parse_post_title(content: Any) -> str | None:
    if isinstance(content, dict):
        return content.get("title") or content.get("youtube_title")
    if isinstance(content, str):
        try:
            import json

            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed.get("title") or parsed.get("youtube_title")
        except Exception:
            return None
    return None


def project_youtube_video_metrics(project_id: str, limit: int = 100) -> list[dict]:
    sb = get_supabase()
    metrics = (
        sb.table("youtube_video_metrics")
        .select(
            "post_id, video_id, checkpoint, views, likes, comments, watch_time_minutes, "
            "average_view_duration_seconds, collected_at"
        )
        .eq("project_id", project_id)
        .order("collected_at", desc=True)
        .limit(limit)
        .execute()
        .data
        or []
    )
    if not metrics:
        return []
    post_ids = [m.get("post_id") for m in metrics if m.get("post_id")]
    posts = (
        sb.table("posts")
        .select("id, post_url, posted_at, content, generating_model")
        .in_("id", post_ids)
        .execute()
        .data
        or []
    )
    post_map = {p.get("id"): p for p in posts if p.get("id")}
    runs = (
        sb.table("audio_generation_runs")
        .select("post_id, script_model, tts_model, tts_voice, created_at")
        .in_("post_id", post_ids)
        .order("created_at", desc=True)
        .execute()
        .data
        or []
    )
    run_map: dict[str, dict] = {}
    for run in runs:
        pid = run.get("post_id")
        if pid and pid not in run_map:
            run_map[pid] = run

    rows: list[dict] = []
    for metric in metrics:
        post = post_map.get(metric.get("post_id")) or {}
        run = run_map.get(metric.get("post_id")) or {}
        title = _parse_post_title(post.get("content")) or "Audio Roundup"
        rows.append(
            {
                **metric,
                "post_url": post.get("post_url"),
                "posted_at": post.get("posted_at"),
                "title": title,
                "script_model": run.get("script_model"),
                "tts_model": run.get("tts_model"),
                "tts_voice": run.get("tts_voice"),
                "generating_model": post.get("generating_model"),
            }
        )
    return rows


def get_youtube_account(project_id: str) -> dict | None:
    sb = get_supabase()
    res = (
        sb.table("youtube_accounts")
        .select("*")
        .eq("project_id", project_id)
        .limit(1)
        .execute()
    )
    return (res.data or [None])[0]


def upsert_youtube_account(project_id: str, refresh_token: str, channel_title: str | None, scopes: list[str] | None) -> dict:
    sb = get_supabase()
    payload = {
        "project_id": project_id,
        "refresh_token": refresh_token.strip(),
        "channel_title": channel_title,
        "scopes": scopes or [],
        "updated_at": _now_iso(),
        "created_at": _now_iso(),
    }
    res = sb.table("youtube_accounts").upsert(payload, on_conflict="project_id").execute()
    return (res.data or [payload])[0]


@dataclass
class ScrapeResult:
    source_id: str
    count: int
    status: str


def scrape_project(project_id: str, max_items: int = 10) -> list[ScrapeResult]:
    sources = [s for s in list_sources(project_id) if s.get("enabled", True)]
    results: list[ScrapeResult] = []
    sb = get_supabase()
    for source in sources:
        if not _should_scrape_source(source):
            source_id = source.get("id")
            if source_id:
                sb.table("sources").update(
                    {"last_status": "skipped", "updated_at": _now_iso()}
                ).eq("id", source_id).execute()
            results.append(ScrapeResult(source_id=source_id or "", count=0, status="skipped"))
            continue
        results.append(scrape_source(source, max_items=max_items))
    return results


def scrape_source(source: dict, max_items: int = 10) -> ScrapeResult:
    source_id = source["id"]
    source_type = (source.get("source_type") or "").lower()
    url = source.get("url") or ""
    config = source.get("config") or {}
    sb = get_supabase()
    status = "ok"
    count = 0
    try:
        if source_type == "reddit":
            count = _scrape_reddit_source(sb, source_id, url, max_items=max_items, config=config)
        elif source_type in {"rss", "youtube"}:
            count = _scrape_rss_source(sb, source_id, url, max_items=max_items, config=config)
        elif source_type in {"page", "website"}:
            count = _scrape_page_source(sb, source_id, url, config=config)
        else:
            status = f"unknown source_type: {source_type}"
    except Exception as exc:
        status = f"error: {exc.__class__.__name__}"
    sb.table("sources").update(
        {
            "last_scraped_at": _now_iso(),
            "last_status": status,
            "updated_at": _now_iso(),
        }
    ).eq("id", source_id).execute()
    return ScrapeResult(source_id=source_id, count=count, status=status)


def _scrape_rss_source(sb: Any, source_id: str, url: str, max_items: int, config: dict | None = None) -> int:
    settings = get_settings()
    kwargs = _request_kwargs(settings, config, accept="application/rss+xml,application/xml,text/xml")
    resp = requests.get(url, **kwargs)
    if resp.status_code in {401, 403}:
        _mark_auth_required(sb, source_id, config, f"http_{resp.status_code}")
        return 0
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    rows: list[dict] = []
    for entry in feed.entries[:max_items]:
        link = entry.get("link") or entry.get("id")
        if not link:
            continue
        summary = entry.get("summary") or ""
        content = summary
        if not content and entry.get("content"):
            content = entry["content"][0].get("value", "")
        published = _to_iso(entry.get("published_parsed") or entry.get("updated_parsed"))
        rows.append(
            {
                "source_id": source_id,
                "title": entry.get("title"),
                "url": link,
                "content": (content or "")[:MAX_CONTENT_CHARS],
                "raw": (summary or "")[:MAX_CONTENT_CHARS],
                "published_at": published,
                "scraped_at": _now_iso(),
            }
        )
    if not rows:
        return 0
    return _upsert_items(sb, rows)


def _scrape_reddit_source(sb: Any, source_id: str, url: str, max_items: int, config: dict | None = None) -> int:
    settings = get_settings()
    listing_url = _normalize_reddit_listing_url(url, max_items=max_items)
    kwargs = _request_kwargs(settings, config, accept="application/json")
    resp = requests.get(listing_url, **kwargs)
    resp.raise_for_status()
    payload = resp.json()
    children = payload.get("data", {}).get("children", []) or []
    rows: list[dict] = []
    for child in children[:max_items]:
        post = child.get("data") or {}
        title = post.get("title") or ""
        link = post.get("url") or ""
        permalink = post.get("permalink") or ""
        reddit_url = f"https://www.reddit.com{permalink}" if permalink else link
        selftext = post.get("selftext") or ""
        image_url = _extract_reddit_image_url(post)
        article_text = ""
        if link and not post.get("is_self") and not image_url:
            article_text = _fetch_article_text(
                link,
                settings,
                config=config,
                source_id=source_id,
                sb=sb,
            )
        caption = caption_image(image_url) if image_url else ""

        content_parts: list[str] = []
        if selftext:
            content_parts.append(selftext)
        if article_text:
            content_parts.append(article_text)
        if caption:
            content_parts.append(f"Image description: {caption}")
        elif image_url:
            content_parts.append(f"Image URL: {image_url}")
        if not content_parts:
            content_parts.append(title)
        content = _truncate("\n\n".join([part for part in content_parts if part]).strip())
        raw = _truncate(
            " | ".join(
                [
                    f"score={post.get('score')}",
                    f"comments={post.get('num_comments')}",
                    f"subreddit={post.get('subreddit')}",
                    f"author={post.get('author')}",
                ]
            )
        )
        rows.append(
            {
                "source_id": source_id,
                "title": title,
                "url": reddit_url or link,
                "content": content,
                "raw": raw,
                "published_at": _to_iso(post.get("created_utc")),
                "scraped_at": _now_iso(),
            }
        )
    if not rows:
        return 0
    return _upsert_items(sb, rows)


def _scrape_page_source(sb: Any, source_id: str, url: str, config: dict | None = None) -> int:
    settings = get_settings()
    kwargs = _request_kwargs(settings, config, accept="text/html")
    resp = requests.get(url, **kwargs)
    if resp.status_code in {401, 403}:
        _mark_auth_required(sb, source_id, config, f"http_{resp.status_code}")
        return 0
    resp.raise_for_status()
    extracted = trafilatura.extract(resp.text) or ""
    reason = _detect_login_required(resp.text, extracted, resp.status_code, url=url)
    if reason:
        _mark_auth_required(sb, source_id, config, reason)
    row = {
        "source_id": source_id,
        "title": url,
        "url": url,
        "content": extracted[:MAX_CONTENT_CHARS],
        "raw": extracted[:MAX_CONTENT_CHARS],
        "published_at": None,
        "scraped_at": _now_iso(),
    }
    return _upsert_items(sb, [row])


def _upsert_items(sb: Any, rows: list[dict]) -> int:
    if not rows:
        return 0
    # Caller injects source_id for each row.
    res = sb.table("source_items").upsert(rows, on_conflict="source_id,url").execute()
    return len(res.data or rows)


def _normalize_article_url(url: str) -> str:
    if not url:
        return url
    parts = urlsplit(url)
    if not parts.scheme or not parts.netloc:
        return url
    filtered = []
    for key, value in parse_qsl(parts.query, keep_blank_values=False):
        key_lower = key.lower()
        if key_lower.startswith("utm_"):
            continue
        if key_lower in {"fbclid", "gclid", "ref", "refsrc"}:
            continue
        filtered.append((key, value))
    query = urlencode(filtered)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, ""))


def _source_website(url: str) -> str:
    return urlparse(url).netloc or "unknown"


def ingest_source_items(limit: int = 20, fetch_full: bool = True, project_id: str | None = None) -> int:
    settings = get_settings()
    sb = get_supabase()
    source_filter: list[str] | None = None
    if project_id:
        sources = (
            sb.table("sources")
            .select("id")
            .eq("project_id", project_id)
            .execute()
            .data
            or []
        )
        source_filter = [s["id"] for s in sources if s.get("id")]
        if not source_filter:
            return 0
    query = (
        sb.table("source_items")
        .select("id, source_id, title, url, content, raw, published_at, scraped_at")
        .order("scraped_at", desc=True)
        .limit(limit)
    )
    if source_filter:
        query = query.in_("source_id", source_filter)
    items = query.execute().data or []
    if not items:
        return 0

    source_ids = [i["source_id"] for i in items if i.get("source_id")]
    source_map: dict[str, dict] = {}
    if source_ids:
        sources = (
            sb.table("sources")
            .select("id, name, config, project_id")
            .in_("id", list({sid for sid in source_ids}))
            .execute()
            .data
            or []
        )
        source_map = {s["id"]: s for s in sources}

    count = 0
    for item in items:
        url = _normalize_article_url(item.get("url") or "")
        if not url:
            continue
        existing = sb.table("articles").select("id").eq("source_url", url).limit(1).execute()
        if existing.data:
            continue
        source = source_map.get(item.get("source_id")) or {}
        config = source.get("config") or {}
        raw_text = (item.get("content") or "").strip()
        if fetch_full:
            try:
                kwargs = _request_kwargs(settings, config, accept="text/html")
                resp = requests.get(url, **kwargs)
                if resp.status_code in {401, 403}:
                    _mark_auth_required(sb, item.get("source_id"), config, f"http_{resp.status_code}")
                elif resp.status_code == 200:
                    extracted = trafilatura.extract(
                        resp.text, include_comments=False, include_tables=False
                    )
                    reason = _detect_login_required(resp.text, extracted, resp.status_code, url=url)
                    if reason:
                        _mark_auth_required(sb, item.get("source_id"), config, reason)
                    if extracted:
                        raw_text = extracted.strip()
            except Exception:
                pass
        if not raw_text:
            raw_text = (item.get("raw") or "").strip()
        if not raw_text:
            continue
        raw_text = _truncate(raw_text, settings.extraction_max_chars)
        row = {
            "source_url": url,
            "source_website": _source_website(url),
            "project_id": source.get("project_id"),
            "source_id": source.get("id"),
            "title": item.get("title"),
            "raw_html": raw_text,
            "content": raw_text,
            "content_hash": _content_hash(raw_text),
            "scraped_at": item.get("scraped_at") or _now_iso(),
            "processed": False,
            "scored": False,
        }
        sb.table("articles").insert(row).execute()
        count += 1
    return count


def check_source_access(source_id: str, sample: int = 3) -> dict:
    source = get_source(source_id)
    if not source:
        return {"status": "not_found"}
    settings = get_settings()
    config = source.get("config") or {}
    source_type = (source.get("source_type") or "").lower()
    url = source.get("url") or ""
    sb = get_supabase()

    urls: list[str] = []
    reason: str | None = None
    try:
        if source_type in {"rss", "youtube"}:
            kwargs = _request_kwargs(settings, config, accept="application/rss+xml,application/xml,text/xml")
            resp = requests.get(url, **kwargs)
            if resp.status_code in {401, 403}:
                reason = f"http_{resp.status_code}"
            else:
                resp.raise_for_status()
                feed = feedparser.parse(resp.text)
                for entry in feed.entries[:sample]:
                    link = entry.get("link") or entry.get("id")
                    if link:
                        urls.append(link)
        elif source_type == "reddit":
            listing_url = _normalize_reddit_listing_url(url, max_items=sample)
            kwargs = _request_kwargs(settings, config, accept="application/json")
            resp = requests.get(listing_url, **kwargs)
            if resp.status_code in {401, 403}:
                reason = f"http_{resp.status_code}"
            else:
                resp.raise_for_status()
                payload = resp.json()
                children = payload.get("data", {}).get("children", []) or []
                for child in children:
                    post = child.get("data") or {}
                    link = post.get("url") or ""
                    if not link:
                        continue
                    if "reddit.com" in urlparse(link).netloc:
                        continue
                    urls.append(link)
                    if len(urls) >= sample:
                        break
        else:
            if url:
                urls.append(url)
    except Exception:
        return {"status": "error"}

    if reason:
        _mark_auth_required(sb, source_id, config, reason)
        return {"status": "login_required", "reason": reason, "checked": urls}

    for target in urls[:sample]:
        if not target or _looks_like_media(target):
            continue
        try:
            kwargs = _request_kwargs(settings, config, accept="text/html")
            resp = requests.get(target, **kwargs)
            if resp.status_code in {401, 403}:
                reason = f"http_{resp.status_code}"
                break
            extracted = trafilatura.extract(resp.text, include_comments=False, include_tables=False) or ""
            reason = _detect_login_required(resp.text, extracted, resp.status_code, url=target)
            if reason:
                break
        except Exception:
            continue

    if reason:
        _mark_auth_required(sb, source_id, config, reason)
        return {"status": "login_required", "reason": reason, "checked": urls}
    _mark_auth_checked(sb, source_id, config, "ok")
    return {"status": "ok", "checked": urls}


def check_project_access(project_id: str, sample: int = 3) -> dict:
    sources = [s for s in list_sources(project_id) if s.get("enabled", True)]
    checked = 0
    flagged = 0
    details: list[dict] = []
    for source in sources:
        checked += 1
        result = check_source_access(source["id"], sample=sample)
        if result.get("status") == "login_required":
            flagged += 1
        details.append({"id": source["id"], "name": source.get("name"), **result})
    return {"checked": checked, "flagged": flagged, "details": details}
