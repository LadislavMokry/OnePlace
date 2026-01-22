from __future__ import annotations

from app.admin import create_source
from app.db import get_supabase


PROJECT_NAME = "TV & Streaming Recaps"

SOURCES: list[dict] = [
    # Core recaps / spoilers (6h)
    {
        "name": "TVLine",
        "source_type": "rss",
        "url": "https://tvline.com/feed/",
        "scrape_interval_hours": 6,
    },
    {
        "name": "TV Insider",
        "source_type": "rss",
        "url": "https://www.tvinsider.com/feed/",
        "scrape_interval_hours": 6,
    },
    {
        "name": "SpoilerTV",
        "source_type": "rss",
        "url": "https://spoilertv.com/feeds/posts/default",
        "scrape_interval_hours": 6,
    },
    {
        "name": "Den of Geek - TV",
        "source_type": "rss",
        "url": "https://www.denofgeek.com/tv/feed/",
        "scrape_interval_hours": 6,
    },
    {
        "name": "Decider",
        "source_type": "rss",
        "url": "https://decider.com/feed/",
        "scrape_interval_hours": 6,
    },
    # Streaming news / industry (12h)
    {
        "name": "What's on Netflix",
        "source_type": "rss",
        "url": "https://www.whats-on-netflix.com/feed/",
        "scrape_interval_hours": 12,
    },
    {
        "name": "TV Series Finale",
        "source_type": "rss",
        "url": "https://tvseriesfinale.com/feed/",
        "scrape_interval_hours": 12,
    },
    {
        "name": "The Wrap",
        "source_type": "rss",
        "url": "https://thewrap.com/feed/",
        "scrape_interval_hours": 12,
    },
    {
        "name": "IndieWire",
        "source_type": "rss",
        "url": "https://indiewire.com/feed/rss",
        "scrape_interval_hours": 12,
    },
    # Release calendar / urgency (24h)
    {
        "name": "What's on Netflix - Leaving Soon",
        "source_type": "rss",
        "url": "https://www.whats-on-netflix.com/leaving-soon/feed/",
        "scrape_interval_hours": 24,
    },
    {
        "name": "NewOnNetflix USA",
        "source_type": "rss",
        "url": "https://usa.newonnetflix.info/feed",
        "scrape_interval_hours": 24,
    },
    # Deeper reviews / explainers (24h)
    {
        "name": "Entertainment Weekly - TV",
        "source_type": "rss",
        "url": "https://feeds-api.dotdashmeredith.com/v1/rss/google/fa742bf3-eccd-4714-ae46-56e7641d1ffc",
        "scrape_interval_hours": 24,
    },
    {
        "name": "Slant Magazine - TV",
        "source_type": "rss",
        "url": "https://slantmagazine.com/category/tv/feed/",
        "scrape_interval_hours": 24,
    },
    {
        "name": "Vulture",
        "source_type": "rss",
        "url": "http://feeds.feedburner.com/nymag/vulture",
        "scrape_interval_hours": 24,
    },
]


def main() -> None:
    sb = get_supabase()
    project = (
        sb.table("projects").select("id, name").eq("name", PROJECT_NAME).limit(1).execute().data
    )
    if not project:
        print(f"project_not_found: {PROJECT_NAME}")
        return
    project_id = project[0]["id"]

    existing = (
        sb.table("sources").select("id, name, url").eq("project_id", project_id).execute().data
        or []
    )
    if existing:
        sb.table("sources").delete().eq("project_id", project_id).execute()
        print(f"deleted_sources={len(existing)}")
    else:
        print("deleted_sources=0")

    created = 0
    for src in SOURCES:
        create_source(project_id, src)
        created += 1
    print(f"created_sources={created}")


if __name__ == "__main__":
    main()
