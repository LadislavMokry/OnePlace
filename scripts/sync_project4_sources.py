from __future__ import annotations

from app.admin import create_source
from app.db import get_supabase


PROJECT_NAME = "Viral / Human-interest"

SOURCES: list[dict] = [
    # Uplifting / human-interest core (6h)
    {
        "name": "Good News Network",
        "source_type": "rss",
        "url": "https://www.goodnewsnetwork.org/feed/",
        "scrape_interval_hours": 6,
    },
    {
        "name": "Upworthy",
        "source_type": "rss",
        "url": "https://upworthy.com/feeds/feed.rss",
        "scrape_interval_hours": 6,
    },
    {
        "name": "Positive News",
        "source_type": "rss",
        "url": "https://www.positive.news/feed/",
        "scrape_interval_hours": 12,
    },
    {
        "name": "Reasons to be Cheerful",
        "source_type": "rss",
        "url": "https://reasonstobecheerful.world/feed",
        "scrape_interval_hours": 12,
    },
    {
        "name": "Sunny Skyz",
        "source_type": "rss",
        "url": "https://feeds.feedburner.com/SunnySkyz",
        "scrape_interval_hours": 6,
    },
    # Quirky / wow (12h)
    {
        "name": "Atlas Obscura",
        "source_type": "rss",
        "url": "https://www.atlasobscura.com/feeds/latest",
        "scrape_interval_hours": 12,
    },
    {
        "name": "Mental Floss",
        "source_type": "rss",
        "url": "https://www.mentalfloss.com/rss.xml",
        "scrape_interval_hours": 12,
    },
    {
        "name": "UPI Odd News",
        "source_type": "rss",
        "url": "https://rss.upi.com/news/odd_news.rss",
        "scrape_interval_hours": 12,
    },
    {
        "name": "Oddity Central",
        "source_type": "rss",
        "url": "https://www.odditycentral.com/feed/",
        "scrape_interval_hours": 12,
    },
    # Viral / community (6h)
    {
        "name": "Bored Panda",
        "source_type": "rss",
        "url": "http://feeds.feedburner.com/BoredPanda",
        "scrape_interval_hours": 6,
    },
    {
        "name": "Good Good Good",
        "source_type": "rss",
        "url": "https://goodgoodgood.co/articles/rss.xml",
        "scrape_interval_hours": 12,
    },
    {
        "name": "This Is Colossal",
        "source_type": "rss",
        "url": "https://www.thisiscolossal.com/feed/",
        "scrape_interval_hours": 12,
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
