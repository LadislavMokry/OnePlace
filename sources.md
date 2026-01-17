- Formula 1 (official): https://www.formula1.com/en/latest/all.xml. (rss.feedspot.com (https://rss.feedspot.com/formula_one_rss_feeds/?utm_source=openai))
- FIA press releases: https://www.fia.com/rss/press-release. (fia.com (https://www.fia.com/rss-feeds?utm_source=openai))
- FIA news: https://www.fia.com/rss/news. (fia.com (https://www.fia.com/rss-feeds?utm_source=openai))
- Motorsport.com F1 news (global): https://www.motorsport.com/rss/f1/news/. (rss.feedspot.com (https://rss.feedspot.com/motorsportdotcom_rss_feeds/?utm_source=openai))
- Autosport F1 news: https://www.autosport.com/rss/f1/news. (rss.feedspot.com (https://rss.feedspot.com/formula_one_rss_feeds/?utm_source=openai))
- F1Technical (technical deep dives): https://www.f1technical.net/rss/news.xml. (rsscatalog.com (https://www.rsscatalog.com/Motorsport?utm_source=openai))
- Optional Spanish feed (still high quality): https://lat.motorsport.com/rss/f1/news/. (lat.motorsport.com (https://lat.motorsport.com/rss/?utm_source=openai))

Reddit sources (type reddit, now pulls most‑upvoted recent posts):

- https://www.reddit.com/r/formula1/ (rl.huuu.biz (https://rl.huuu.biz/r/Formula1?utm_source=openai))
- https://www.reddit.com/r/F1Technical/ (rl.huuu.biz (https://rl.huuu.biz/r/F1Technical?utm_source=openai))
- Optional broader F1 community: https://www.reddit.com/r/GrandPrixRacing/ (redditwiki.com (https://redditwiki.com/r-grandprixracing/?utm_source=openai))

How the new Reddit pipeline works

- Defaults to top posts from the last day (t=day). To change: append ?t=week or use /new/ in the URL.
- For link posts, it fetches and extracts article text with trafilatura.
- For image posts, it can generate a caption via OpenAI (optional).

Enable image understanding by adding this to .env.local:

ENABLE_IMAGE_CAPTION=true
IMAGE_CAPTION_MODEL=gpt-4o-mini

If you want me to add these sources to your new Slovak F1 project right now, tell me the project name (or say “create a new one”) and whether you want the Re
