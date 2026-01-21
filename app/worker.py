import argparse
import time

from pathlib import Path

from .config import get_settings
from .admin import ingest_source_items, list_projects, scrape_project
from .media.audio import render_audio_roundup
from .media.roundup_video import render_audio_roundup_video
from .media.short_video import render_short_video
from .media.paths import roundup_audio_path, roundup_video_path, short_video_path
from .pipeline import (
    fetch_latest_audio_roundup,
    fetch_latest_selected_video,
    cleanup_old_data,
    run_pipeline_all,
    run_project_pipeline,
    run_audio_roundup,
    run_extraction,
    run_first_judge,
    run_generation,
    run_second_judge,
    update_post_media,
)


def run_scrape_sources(project_id: str | None = None, max_items: int = 10) -> dict:
    results: list[dict] = []
    if project_id:
        scrape_results = scrape_project(project_id, max_items=max_items)
        results.append(
            {
                "project_id": project_id,
                "results": [r.__dict__ for r in scrape_results],
            }
        )
    else:
        projects = list_projects()
        for project in projects:
            pid = project.get("id")
            if not pid:
                continue
            scrape_results = scrape_project(pid, max_items=max_items)
            results.append(
                {
                    "project_id": pid,
                    "name": project.get("name"),
                    "results": [r.__dict__ for r in scrape_results],
                }
            )
    total = sum(r.get("count", 0) for row in results for r in row.get("results", []))
    return {"total": total, "projects": results}


def main() -> None:
    parser = argparse.ArgumentParser(description="Background worker")
    sub = parser.add_subparsers(dest="command", required=True)

    scrape_parser = sub.add_parser("scrape", help="Scrape configured sources once")
    scrape_parser.add_argument("--project-id", type=str, default=None, help="Project ID filter")
    scrape_parser.add_argument("--max-items", type=int, default=10, help="Max items per source")
    ingest_sources = sub.add_parser("ingest-sources", help="Ingest source items into articles")
    ingest_sources.add_argument("--limit", type=int, default=20, help="Max source items to ingest")
    ingest_sources.add_argument("--project-id", type=str, default=None, help="Project ID filter")
    ingest_sources.add_argument(
        "--no-fetch", action="store_true", help="Use stored excerpts without fetching full pages"
    )

    sub.add_parser("extract", help="Run extraction once")
    sub.add_parser("judge", help="Run first judge once")
    sub.add_parser("generate", help="Run generation once")
    sub.add_parser("second-judge", help="Run second judge once")
    audio_roundup = sub.add_parser("audio-roundup", help="Run audio roundup once")
    audio_roundup.add_argument("--project-id", type=str, default=None, help="Project ID for language settings")
    audio_roundup.add_argument("--language", type=str, default=None, help="Override language (en, es, sk)")
    sub.add_parser("render-audio-roundup", help="Render latest audio roundup to MP3")
    sub.add_parser("render-audio-roundup-video", help="Render latest audio roundup to MP4")
    sub.add_parser("render-video", help="Render latest selected video to MP4")
    pipeline_parser = sub.add_parser("pipeline", help="Run full pipeline per project")
    pipeline_parser.add_argument("--project-id", type=str, default=None, help="Project ID filter")
    pipeline_parser.add_argument("--max-items", type=int, default=10, help="Max items per source")
    cleanup_parser = sub.add_parser("cleanup", help="Delete old source items and wipe unusable content")
    cleanup_parser.add_argument("--hours", type=int, default=48, help="Age threshold in hours")
    cleanup_parser.add_argument(
        "--no-legacy",
        action="store_true",
        help="Skip deleting legacy category_pages and article_urls",
    )
    cleanup_parser.add_argument(
        "--no-wipe",
        action="store_true",
        help="Skip wiping unusable article content",
    )

    loop_parser = sub.add_parser("scrape-loop", help="Scrape on an interval")
    loop_parser.add_argument("--interval", type=int, default=3600, help="Seconds between runs")
    loop_parser.add_argument("--project-id", type=str, default=None, help="Project ID filter")
    loop_parser.add_argument("--max-items", type=int, default=10, help="Max items per source")

    extract_loop = sub.add_parser("extract-loop", help="Extraction on an interval")
    extract_loop.add_argument("--interval", type=int, default=600, help="Seconds between runs")

    judge_loop = sub.add_parser("judge-loop", help="First judge on an interval")
    judge_loop.add_argument("--interval", type=int, default=900, help="Seconds between runs")

    gen_loop = sub.add_parser("generate-loop", help="Generation on an interval")
    gen_loop.add_argument("--interval", type=int, default=1200, help="Seconds between runs")

    second_loop = sub.add_parser("second-judge-loop", help="Second judge on an interval")
    second_loop.add_argument("--interval", type=int, default=1800, help="Seconds between runs")

    args = parser.parse_args()

    if args.command == "scrape":
        result = run_scrape_sources(project_id=args.project_id, max_items=args.max_items)
        print(f"scraped_total={result.get('total', 0)}")
        return
    if args.command == "ingest-sources":
        count = ingest_source_items(limit=args.limit, fetch_full=not args.no_fetch, project_id=args.project_id)
        print(f"ingested_sources={count}")
        return

    if args.command == "extract":
        count = run_extraction()
        print(f"extracted={count}")
        return

    if args.command == "judge":
        count = run_first_judge()
        print(f"judged={count}")
        return

    if args.command == "generate":
        count = run_generation()
        print(f"generated_posts={count}")
        return

    if args.command == "second-judge":
        count = run_second_judge()
        print(f"second_judged={count}")
        return
    if args.command == "audio-roundup":
        count = run_audio_roundup(project_id=args.project_id, language=args.language)
        print(f"audio_roundup={count}")
        return
    if args.command == "render-audio-roundup":
        settings = get_settings()
        row = fetch_latest_audio_roundup()
        if not row:
            print("audio_roundup_rendered=0")
            return
        content = row.get("content") or {}
        dialogue = content.get("dialogue") or []
        out_dir = Path(settings.media_output_dir)
        out_path = roundup_audio_path(out_dir, row["id"])
        render_audio_roundup(dialogue, out_path)
        print(f"audio_roundup_rendered=1 path={out_path}")
        return
    if args.command == "render-audio-roundup-video":
        settings = get_settings()
        row = fetch_latest_audio_roundup()
        if not row:
            print("audio_roundup_video_rendered=0")
            return
        content = row.get("content") or {}
        out_dir = Path(settings.media_output_dir)
        out_path = roundup_video_path(out_dir, row["id"])
        render_audio_roundup_video(content, row["id"], out_path)
        print(f"audio_roundup_video_rendered=1 path={out_path}")
        return
    if args.command == "render-video":
        settings = get_settings()
        row = fetch_latest_selected_video()
        if not row:
            print("video_rendered=0")
            return
        content = row.get("content") or {}
        out_dir = Path(settings.media_output_dir)
        out_path = short_video_path(out_dir, row["id"])
        render_short_video(content, out_path)
        update_post_media(row["id"], str(out_path))
        print(f"video_rendered=1 path={out_path}")
        return
    if args.command == "pipeline":
        if args.project_id:
            results = run_project_pipeline(args.project_id, max_items=args.max_items)
            print(f"pipeline_project={args.project_id} results={results}")
        else:
            results = run_pipeline_all(max_items=args.max_items)
            print(f"pipeline_all count={len(results)}")
        return
    if args.command == "cleanup":
        results = cleanup_old_data(
            hours=args.hours,
            delete_legacy=not args.no_legacy,
            wipe_unusable=not args.no_wipe,
        )
        print("cleanup=" + ",".join([f"{k}={v}" for k, v in results.items()]))
        return

    if args.command == "scrape-loop":
        while True:
            result = run_scrape_sources(project_id=args.project_id, max_items=args.max_items)
            print(f"scraped_total={result.get('total', 0)}")
            time.sleep(args.interval)

    if args.command == "extract-loop":
        while True:
            count = run_extraction()
            print(f"extracted={count}")
            time.sleep(args.interval)

    if args.command == "judge-loop":
        while True:
            count = run_first_judge()
            print(f"judged={count}")
            time.sleep(args.interval)

    if args.command == "generate-loop":
        while True:
            count = run_generation()
            print(f"generated_posts={count}")
            time.sleep(args.interval)

    if args.command == "second-judge-loop":
        while True:
            count = run_second_judge()
            print(f"second_judged={count}")
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
