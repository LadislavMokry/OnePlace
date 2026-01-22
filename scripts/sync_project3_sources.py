from __future__ import annotations

from app.admin import create_source
from app.db import get_supabase


PROJECT_NAME = "Sports (results + storylines)"

SOURCES: list[dict] = [
    # Multi-sport / breaking (6h)
    {
        "name": "ESPN - Top Headlines",
        "source_type": "rss",
        "url": "https://www.espn.com/espn/rss/news",
        "scrape_interval_hours": 6,
    },
    {
        "name": "CBS Sports - Headlines",
        "source_type": "rss",
        "url": "https://www.cbssports.com/rss/headlines/",
        "scrape_interval_hours": 6,
    },
    {
        "name": "Yahoo Sports - Top",
        "source_type": "rss",
        "url": "https://sports.yahoo.com/top/rss.xml",
        "scrape_interval_hours": 6,
    },
    {
        "name": "Yardbarker",
        "source_type": "rss",
        "url": "https://www.yardbarker.com/rss/sport",
        "scrape_interval_hours": 6,
    },
    # NFL core (6h)
    {
        "name": "NBC Sports - NFL",
        "source_type": "rss",
        "url": "https://www.nbcsports.com/nfl.atom",
        "scrape_interval_hours": 6,
    },
    {
        "name": "ESPN - NFL",
        "source_type": "rss",
        "url": "https://www.espn.com/espn/rss/nfl/news",
        "scrape_interval_hours": 6,
    },
    {
        "name": "CBS Sports - NFL",
        "source_type": "rss",
        "url": "https://www.cbssports.com/rss/headlines/nfl",
        "scrape_interval_hours": 6,
    },
    # NBA core (6h)
    {
        "name": "ClutchPoints",
        "source_type": "rss",
        "url": "https://clutchpoints.com/feed",
        "scrape_interval_hours": 6,
    },
    {
        "name": "ESPN - NBA",
        "source_type": "rss",
        "url": "https://www.espn.com/espn/rss/nba/news",
        "scrape_interval_hours": 6,
    },
    {
        "name": "CBS Sports - NBA",
        "source_type": "rss",
        "url": "https://www.cbssports.com/rss/headlines/nba",
        "scrape_interval_hours": 6,
    },
    # MLB/NHL seasonal (12h)
    {
        "name": "MLB Trade Rumors",
        "source_type": "rss",
        "url": "https://www.mlbtraderumors.com/feed",
        "scrape_interval_hours": 12,
    },
    {
        "name": "ESPN - NHL",
        "source_type": "rss",
        "url": "https://www.espn.com/espn/rss/nhl/news",
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
