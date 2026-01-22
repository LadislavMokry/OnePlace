from datetime import datetime, timezone, timedelta
import hashlib
import re

from app.ai.audio_roundup import generate_audio_roundup
from app.ai.extract import extract_summary
from app.ai.first_judge import default_format_rules, judge_summary
from app.ai.generate import generate_video_variant, generation_models
from app.ai.second_judge import pick_winner
from app.admin import ingest_source_items, list_projects, scrape_project
from app.config import get_settings
from app.db import get_supabase


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _content_hash(text: str | None) -> str | None:
    if not text:
        return None
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    if not normalized:
        return None
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def fetch_unprocessed(limit: int = 20, project_id: str | None = None) -> list[dict]:
    sb = get_supabase()
    query = (
        sb.table("articles")
        .select("id, raw_html, title, source_url, content_hash")
        .eq("processed", False)
        .limit(limit)
    )
    if project_id:
        query = query.eq("project_id", project_id)
    resp = query.execute()
    return resp.data or []


def mark_processed(
    article_id: str,
    summary: str,
    title: str | None = None,
    content: str | None = None,
    content_hash: str | None = None,
) -> None:
    sb = get_supabase()
    update = {"summary": summary, "processed": True, "scraped_at": _now()}
    if title:
        update["title"] = title
    if content:
        update["content"] = content
    if content_hash:
        update["content_hash"] = content_hash
    sb.table("articles").update(update).eq("id", article_id).execute()


def run_extraction(limit: int = 3, project_id: str | None = None) -> int:
    items = fetch_unprocessed(limit=limit, project_id=project_id)
    count = 0
    for item in items:
        raw = item.get("raw_html") or ""
        if not raw.strip():
            continue
        result = extract_summary(raw)
        summary = result.get("summary") or ""
        title = result.get("title")
        content = result.get("content")
        content_hash = item.get("content_hash") or _content_hash(content or raw)
        if summary:
            mark_processed(item["id"], summary, title, content, content_hash)
            count += 1
    return count


def fetch_unscored(limit: int = 20, project_id: str | None = None) -> list[dict]:
    sb = get_supabase()
    query = (
        sb.table("articles")
        .select("id, summary")
        .eq("processed", True)
        .eq("scored", False)
        .limit(limit)
    )
    if project_id:
        query = query.eq("project_id", project_id)
    resp = query.execute()
    return resp.data or []


def mark_scored(article_id: str, score: int, formats: list[str]) -> None:
    sb = get_supabase()
    sb.table("articles").update(
        {
            "judge_score": score,
            "format_assignments": formats,
            "scored": True,
        }
    ).eq("id", article_id).execute()


def run_first_judge(limit: int = 20, project_id: str | None = None) -> int:
    settings = get_settings()
    items = fetch_unscored(limit=limit, project_id=project_id)
    count = 0
    for item in items:
        summary = item.get("summary") or ""
        if not summary:
            continue
        result = judge_summary(summary)
        score = int(result.get("score", 0))
        formats = ["video"] if score >= settings.video_min_score else []
        mark_scored(item["id"], score, formats)
        count += 1
    return count


def fetch_ready_for_generation(limit: int = 10, project_id: str | None = None) -> list[dict]:
    sb = get_supabase()
    query = (
        sb.table("articles")
        .select("id, content, judge_score, project_id")
        .eq("scored", True)
        .eq("unusable", False)
        .limit(limit)
    )
    if project_id:
        query = query.eq("project_id", project_id)
    resp = query.execute()
    return resp.data or []


def has_video_posts(article_id: str) -> bool:
    sb = get_supabase()
    resp = (
        sb.table("posts")
        .select("id")
        .eq("article_id", article_id)
        .eq("content_type", "video")
        .limit(1)
        .execute()
    )
    return bool(resp.data)


def insert_video_post(article_id: str, model: str, content: dict) -> int:
    sb = get_supabase()
    row = {
        "article_id": article_id,
        "platform": "tiktok",
        "content_type": "video",
        "generating_model": model,
        "content": content,
    }
    resp = sb.table("posts").insert(row).execute()
    return len(resp.data or [])


def run_generation(limit: int = 10, project_id: str | None = None) -> int:
    settings = get_settings()
    models = generation_models()
    if not models:
        return 0
    model = models[0]
    items = fetch_ready_for_generation(limit=limit, project_id=project_id)
    count = 0
    language_cache: dict[str, str | None] = {}
    prompt_cache: dict[str, dict] = {}
    for item in items:
        if has_video_posts(item["id"]):
            continue
        score = int(item.get("judge_score") or 0)
        if score < settings.video_min_score:
            continue
        content = (item.get("content") or "").strip()
        if not content:
            continue
        language = None
        prompt_extra = None
        project_ref = item.get("project_id")
        if project_ref:
            if project_ref not in language_cache:
                language_cache[project_ref] = _project_language(project_ref)
            if project_ref not in prompt_cache:
                prompt_cache[project_ref] = _project_prompts(project_ref)
            language = language_cache.get(project_ref)
            prompt_extra = (prompt_cache.get(project_ref) or {}).get("video_prompt_extra")
        for variant_id in range(1, settings.generation_variants + 1):
            variant = generate_video_variant(
                content,
                model,
                variant_id,
                language=language,
                extra_prompt=prompt_extra,
            )
            count += insert_video_post(item["id"], model, variant)
    return count


def _project_thresholds(project_id: str | None) -> tuple[int, int]:
    if not project_id:
        return (5, 48)
    sb = get_supabase()
    resp = (
        sb.table("projects")
        .select("unusable_score_threshold, unusable_age_hours")
        .eq("id", project_id)
        .limit(1)
        .execute()
    )
    data = resp.data or []
    if not data:
        return (5, 48)
    row = data[0]
    score = int(row.get("unusable_score_threshold") or 5)
    hours = int(row.get("unusable_age_hours") or 48)
    return (score, hours)


def mark_low_score_unusable(project_id: str) -> int:
    sb = get_supabase()
    score_threshold, age_hours = _project_thresholds(project_id)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=age_hours)
    items = (
        sb.table("articles")
        .select("id, judge_score, scraped_at")
        .eq("project_id", project_id)
        .eq("scored", True)
        .eq("unusable", False)
        .lt("judge_score", score_threshold)
        .lt("scraped_at", cutoff.isoformat())
        .execute()
        .data
        or []
    )
    count = 0
    for item in items:
        sb.table("articles").update(
            {
                "unusable": True,
                "unusable_reason": f"low_score_age(score<{score_threshold},>{age_hours}h)",
                "unusable_at": _now(),
            }
        ).eq("id", item["id"]).execute()
        count += 1
    return count


def dedupe_articles(project_id: str) -> int:
    sb = get_supabase()
    items = (
        sb.table("articles")
        .select("id, content_hash, judge_score, scraped_at, unusable")
        .eq("project_id", project_id)
        .eq("unusable", False)
        .neq("content_hash", None)
        .execute()
        .data
        or []
    )
    if not items:
        return 0
    groups: dict[str, list[dict]] = {}
    for item in items:
        h = item.get("content_hash")
        if not h:
            continue
        groups.setdefault(h, []).append(item)
    count = 0
    for h, group in groups.items():
        if len(group) <= 1:
            continue
        def key(row: dict) -> tuple[int, str]:
            score = int(row.get("judge_score") or 0)
            scraped = row.get("scraped_at") or ""
            return (score, scraped)
        group_sorted = sorted(group, key=key, reverse=True)
        keep = group_sorted[0]
        for dup in group_sorted[1:]:
            sb.table("articles").update(
                {
                    "unusable": True,
                    "unusable_reason": "duplicate",
                    "duplicate_of": keep["id"],
                    "unusable_at": _now(),
                }
            ).eq("id", dup["id"]).execute()
            count += 1
    return count


def fetch_for_second_judge(limit: int = 20) -> list[dict]:
    sb = get_supabase()
    resp = (
        sb.table("posts")
        .select("id, article_id, content_type, generating_model, content, selected")
        .eq("selected", False)
        .eq("content_type", "video")
        .limit(limit)
        .execute()
    )
    return resp.data or []


def group_versions(items: list[dict]) -> dict:
    grouped: dict = {}
    for item in items:
        key = (item["article_id"], item["content_type"])
        content = item.get("content") or {}
        if isinstance(content, str):
            try:
                import json

                content = json.loads(content)
            except json.JSONDecodeError:
                content = {}
        variant_id = None
        if isinstance(content, dict):
            variant_id = content.get("variant_id")
        grouped.setdefault(key, []).append(
            {
                "id": item["id"],
                "model": item["generating_model"],
                "variant_id": variant_id,
                "content": content,
            }
        )
    return grouped


def mark_post_selected(post_id: str) -> None:
    sb = get_supabase()
    sb.table("posts").update({"selected": True}).eq("id", post_id).execute()


def update_model_performance(model: str, content_type: str, winner: bool) -> None:
    sb = get_supabase()
    try:
        sb.rpc(
            "update_model_performance",
            {"p_model_name": model, "p_content_type": content_type, "p_is_winner": winner},
        ).execute()
    except Exception:
        # If RPC not available, skip silently for MVP
        return


def run_second_judge(limit: int = 20) -> int:
    items = fetch_for_second_judge(limit=limit)
    grouped = group_versions(items)
    count = 0
    for (article_id, fmt), versions in grouped.items():
        decision = pick_winner(fmt, versions)
        winner_variant = decision.get("winner_variant") or decision.get("winner")
        # pick matching post id by variant
        winner_post = next(
            (v for v in versions if v.get("variant_id") == winner_variant), None
        )
        if not winner_post:
            winner_post = versions[0]
        mark_post_selected(winner_post["id"])
        for v in versions:
            update_model_performance(v["model"], fmt, v["id"] == winner_post["id"])
        count += 1
    return count


def fetch_for_audio_roundup(
    limit: int = 5, hours: int = 24, project_id: str | None = None
) -> list[dict]:
    sb = get_supabase()
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = (
        sb.table("articles")
        .select("id, title, summary, content, judge_score, scraped_at")
        .eq("processed", True)
        .eq("scored", True)
        .eq("unusable", False)
        .gte("scraped_at", since.isoformat())
        .order("judge_score", desc=True)
        .limit(limit * 3)
    )
    if project_id:
        query = query.eq("project_id", project_id)
    query = query.is_("duplicate_of", "null")
    items = query.execute().data or []
    if not items:
        return []
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
    filtered = [i for i in items if i["id"] not in used_ids]
    return filtered[:limit]


def insert_audio_roundup(model: str, content: dict) -> dict | None:
    sb = get_supabase()
    row = {
        "article_id": None,
        "platform": "youtube",
        "content_type": "audio_roundup",
        "generating_model": model,
        "content": content,
    }
    resp = sb.table("posts").insert(row).execute()
    data = resp.data or []
    return data[0] if data else None


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


def _project_prompts(project_id: str) -> dict:
    sb = get_supabase()
    try:
        resp = (
            sb.table("projects")
            .select("video_prompt_extra,audio_roundup_prompt_extra")
            .eq("id", project_id)
            .limit(1)
            .execute()
        )
    except Exception:
        return {}
    data = resp.data or []
    return data[0] if data else {}


def run_audio_roundup(project_id: str | None = None, language: str | None = None) -> int:
    settings = get_settings()
    prompt_extra = None
    if project_id and not language:
        language = _project_language(project_id)
    if project_id:
        prompt_extra = _project_prompts(project_id).get("audio_roundup_prompt_extra")
    items = fetch_for_audio_roundup(
        limit=settings.audio_roundup_size, hours=settings.audio_roundup_hours, project_id=project_id
    )
    if not items:
        return 0
    stories = []
    for item in items:
        summary = item.get("summary") or ""
        content = item.get("content") or ""
        stories.append(
            {
                "title": item.get("title"),
                "summary": summary,
                "content": content if content.strip() else summary,
            }
        )
    content = generate_audio_roundup(stories, language=language, extra_prompt=prompt_extra)
    post = insert_audio_roundup(settings.audio_roundup_model, content)
    if post:
        usage_rows = [
            {
                "article_id": item.get("id"),
                "usage_type": "audio_roundup",
                "post_id": post.get("id"),
            }
            for item in items
            if item.get("id")
        ]
        if usage_rows:
            sb = get_supabase()
            sb.table("article_usage").insert(usage_rows).execute()
        return 1
    return 0


def fetch_latest_audio_roundup() -> dict | None:
    sb = get_supabase()
    resp = (
        sb.table("posts")
        .select("id, content")
        .eq("content_type", "audio_roundup")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    data = resp.data or []
    return data[0] if data else None


def fetch_latest_audio_roundup_for_project(project_id: str) -> dict | None:
    sb = get_supabase()
    resp = (
        sb.table("posts")
        .select("id, content, created_at")
        .eq("content_type", "audio_roundup")
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    candidates = resp.data or []
    if not candidates:
        return None
    post_ids = [row.get("id") for row in candidates if row.get("id")]
    if not post_ids:
        return None
    usage = (
        sb.table("article_usage")
        .select("post_id, article_id")
        .in_("post_id", post_ids)
        .execute()
        .data
        or []
    )
    if not usage:
        return None
    article_ids = [row.get("article_id") for row in usage if row.get("article_id")]
    if not article_ids:
        return None
    articles = (
        sb.table("articles")
        .select("id, project_id")
        .in_("id", article_ids)
        .execute()
        .data
        or []
    )
    project_lookup = {row["id"]: row.get("project_id") for row in articles if row.get("id")}
    post_projects: dict[str, set[str]] = {}
    for row in usage:
        post_id = row.get("post_id")
        article_id = row.get("article_id")
        if not post_id or not article_id:
            continue
        project = project_lookup.get(article_id)
        if not project:
            continue
        post_projects.setdefault(post_id, set()).add(project)

    for row in candidates:
        post_id = row.get("id")
        projects = post_projects.get(post_id) or set()
        if project_id in projects:
            return row
    return None


def fetch_latest_selected_video() -> dict | None:
    sb = get_supabase()
    resp = (
        sb.table("posts")
        .select("id, content")
        .eq("content_type", "video")
        .eq("selected", True)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    data = resp.data or []
    return data[0] if data else None


def update_post_media(post_id: str, media_url: str) -> None:
    sb = get_supabase()
    sb.table("posts").update({"media_urls": [media_url]}).eq("id", post_id).execute()


def _chunk_ids(values: list[str], size: int = 200) -> list[list[str]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def cleanup_old_data(
    hours: int = 48,
    delete_legacy: bool = True,
    wipe_unusable: bool = True,
) -> dict:
    sb = get_supabase()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    cutoff_iso = cutoff.isoformat()
    summary: dict[str, int] = {}

    if delete_legacy:
        resp = sb.table("category_pages").delete().lt("scraped_at", cutoff_iso).execute()
        summary["category_pages_deleted"] = len(resp.data or [])
        resp = sb.table("article_urls").delete().lt("discovered_at", cutoff_iso).execute()
        summary["article_urls_deleted"] = len(resp.data or [])

    resp = sb.table("source_items").delete().lt("scraped_at", cutoff_iso).execute()
    summary["source_items_deleted"] = len(resp.data or [])

    if not wipe_unusable:
        return summary

    ids: list[str] = []
    page_size = 500
    offset = 0
    while True:
        resp = (
            sb.table("articles")
            .select("id")
            .eq("unusable", True)
            .lt("scraped_at", cutoff_iso)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        batch = resp.data or []
        if not batch:
            break
        ids.extend([row["id"] for row in batch if row.get("id")])
        if len(batch) < page_size:
            break
        offset += page_size

    if not ids:
        summary["articles_wiped"] = 0
        return summary

    posts = (
        sb.table("posts")
        .select("article_id")
        .in_("article_id", ids)
        .execute()
        .data
        or []
    )
    usage = (
        sb.table("article_usage")
        .select("article_id")
        .in_("article_id", ids)
        .execute()
        .data
        or []
    )
    blocked = {row["article_id"] for row in posts if row.get("article_id")}
    blocked.update({row["article_id"] for row in usage if row.get("article_id")})

    to_wipe = [article_id for article_id in ids if article_id not in blocked]
    for chunk in _chunk_ids(to_wipe, size=200):
        sb.table("articles").update({"raw_html": None, "content": None}).in_("id", chunk).execute()

    summary["articles_wiped"] = len(to_wipe)
    return summary


def log_pipeline_run(
    project_id: str | None,
    results: dict,
    status: str = "ok",
    started_at: str | None = None,
    finished_at: str | None = None,
) -> None:
    sb = get_supabase()
    payload = {
        "project_id": project_id,
        "run_type": "pipeline",
        "status": status,
        "scrape_count": len(results.get("scrape") or []),
        "ingest_count": int(results.get("ingest") or 0),
        "extract_count": int(results.get("extract") or 0),
        "judge_count": int(results.get("judge") or 0),
        "dedupe_count": int(results.get("dedupe") or 0),
        "unusable_count": int(results.get("unusable") or 0),
        "started_at": started_at or _now(),
        "finished_at": finished_at or _now(),
    }
    try:
        sb.table("pipeline_runs").insert(payload).execute()
    except Exception:
        # Logging is best-effort; do not break pipeline on insert failure.
        return


def run_project_pipeline(project_id: str, max_items: int = 10) -> dict:
    started_at = _now()
    results: dict = {}
    scrape_results = scrape_project(project_id, max_items=max_items)
    results["scrape"] = [r.__dict__ for r in scrape_results]
    results["ingest"] = ingest_source_items(limit=50, fetch_full=True, project_id=project_id)
    extract_total = 0
    judge_total = 0
    max_extract = 200
    max_judge = 500
    while extract_total < max_extract:
        count = run_extraction(limit=20, project_id=project_id)
        extract_total += count
        if count == 0:
            break
    while judge_total < max_judge:
        count = run_first_judge(limit=50, project_id=project_id)
        judge_total += count
        if count == 0:
            break
    results["extract"] = extract_total
    results["judge"] = judge_total
    results["dedupe"] = dedupe_articles(project_id)
    results["unusable"] = mark_low_score_unusable(project_id)
    finished_at = _now()
    log_pipeline_run(project_id, results, started_at=started_at, finished_at=finished_at)
    return results


def run_pipeline_all(max_items: int = 10) -> list[dict]:
    results: list[dict] = []
    projects = list_projects()
    for project in projects:
        project_id = project.get("id")
        if not project_id:
            continue
        results.append(
            {
                "project_id": project_id,
                "name": project.get("name"),
                "results": run_project_pipeline(project_id, max_items=max_items),
            }
        )
    return results
