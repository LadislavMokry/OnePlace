from __future__ import annotations

from app.admin import create_source
from app.db import get_supabase


PROJECT_NAME = "Celebrities / Entertainment"

SOURCES: list[dict] = [
    {
        "name": "TMZ",
        "source_type": "rss",
        "url": "https://www.tmz.com/rss.xml",
        "scrape_interval_hours": 6,
    },
    {
        "name": "Page Six (Gossip)",
        "source_type": "rss",
        "url": "https://pagesix.com/gossip/feed/",
        "scrape_interval_hours": 6,
    },
    {
        "name": "People - Celebrity",
        "source_type": "rss",
        "url": "https://feeds-api.dotdashmeredith.com/v1/rss/google/79365970-e87d-4fb6-966a-1c657b08f44f",
        "scrape_interval_hours": 6,
    },
    {
        "name": "Us Weekly - Celebrity News",
        "source_type": "rss",
        "url": "https://www.usmagazine.com/category/celebrity-news/feed/",
        "scrape_interval_hours": 6,
    },
    {
        "name": "The Shade Room",
        "source_type": "rss",
        "url": "https://theshaderoom.com/feed/",
        "scrape_interval_hours": 6,
    },
    {
        "name": "Deadline",
        "source_type": "rss",
        "url": "https://deadline.com/feed/",
        "scrape_interval_hours": 6,
    },
    {
        "name": "Variety",
        "source_type": "rss",
        "url": "https://variety.com/feed/",
        "scrape_interval_hours": 6,
    },
    {
        "name": "The Hollywood Reporter",
        "source_type": "rss",
        "url": "https://hollywoodreporter.com/feed/",
        "scrape_interval_hours": 12,
    },
    {
        "name": "E! Online",
        "source_type": "rss",
        "url": "https://eonline.com/rss/",
        "scrape_interval_hours": 12,
    },
    {
        "name": "Entertainment Tonight",
        "source_type": "rss",
        "url": "https://etonline.com/news/rss",
        "scrape_interval_hours": 12,
    },
    {
        "name": "Just Jared",
        "source_type": "rss",
        "url": "https://justjared.com/feed/",
        "scrape_interval_hours": 12,
    },
    {
        "name": "Billboard",
        "source_type": "rss",
        "url": "https://www.billboard.com/feed/",
        "scrape_interval_hours": 24,
    },
    {
        "name": "Rolling Stone - Music",
        "source_type": "rss",
        "url": "https://www.rollingstone.com/music/feed/",
        "scrape_interval_hours": 24,
    },
    {
        "name": "BuzzFeed Celebrity",
        "source_type": "rss",
        "url": "https://www.buzzfeed.com/celebrity.xml",
        "scrape_interval_hours": 24,
    },
    {
        "name": "Uproxx - Music",
        "source_type": "rss",
        "url": "https://uproxx.com/music/feed/",
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
