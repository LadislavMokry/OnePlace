Here is a curated list of high-quality, scrape-friendly sources designed to fuel a viral, human-interest content automation system.

These sources were selected because they provide narrative depth (articles 300–800 words), which is critical for scripting a 7–10 minute podcast, rather than just providing a headline or an image.

Recommended Source Table
Source Name	Category	Feed URL	Notes
Good News Network	Uplifting / Global Wins	https://www.goodnewsnetwork.org/feed/	Gold Standard. High narrative volume. Excellent for scripting specific "hero" segments. WordPress-based structure is very easy to scrape.
InspireMore	Human-interest / Viral	https://www.inspiremore.com/feed/	High Emotion. Focuses on teachers, parents, and kids doing amazing things. Perfect for the "tear-jerker" hook. High frequency.
Sunny Skyz	Uplifting / Community	https://www.sunnyskyz.com/feed.php	Community Focused. Covers small-town wins and neighborly acts. Very clean text, minimal ads, easy to parse.
Atlas Obscura	Quirky / "Wow" Moments	https://www.atlasobscura.com/feeds/latest	Narrative Heavy. Excellent for the "weird history" or "strange places" segment of the podcast. Stories are long enough to fill 5 minutes alone.
Tank's Good News	Viral / Pop Culture	https://tanksgoodnews.com/feed/	Gen Z/Millennial Appeal. Founded by an influencer (Tank Sinatra). content is curated specifically for virality/social sharing.
Love Meow	Rescues / Animals	https://www.lovemeow.com/feeds/posts/default	Animal Hooks. Focuses on stray rescues and foster stories. Animal content has the highest "hook" rate on TikTok.
My Modern Met	Quirky / Creative	https://mymodernmet.com/feed/	Visual/Creative. Covers artists, photographers, and accidental discoveries. Good for "You won't believe what this person built" stories.
Laughing Squid	Quirky / Viral	https://laughingsquid.com/feed/	Oddities. Covers weird tech, strange art, and funny internet culture. Good for a lighter, faster-paced segment at the end of the pod.
Mental Floss	Quirky / Educational	https://www.mentalfloss.com/rss.xml	Trivia/Deep Dives. Excellent for "Did you know?" segments. Very well-researched, providing plenty of factual meat for a podcast script.
Positive News	Uplifting / Societal	https://www.positive.news/feed/	Journalistic Tone. Slightly more serious but very high quality. Good for a "Science of Happiness" or "Solution Journalism" segment.
Strategy Implementation Tips

For your automation pipeline to successfully convert these into TikTok hooks and Podcast scripts, consider the following processing logic:

The Hook (TikTok/Reels):

Logic: Extract the <title> and the first <img> from the feed.

Automation: Use the first paragraph of the content (usually the "lead") to generate a 15-second script using an LLM.

Example Hook Source: Tank's Good News or InspireMore (highly visual/emotional).

The Meat (Podcast Segment):

Logic: These RSS feeds usually provide full text or a substantial summary.

Automation: Combine Atlas Obscura (for a weird fact) + Good News Network (for the main story) to create a varied 7-minute episode flow.

Flow: Intro (Hook) -> Main Story (Good News Network) -> Weird Break (Atlas Obscura) -> Viewer Mail/Social Highlight (InspireMore).

Scraping Note:

Most of these are WordPress-based. If the RSS feed truncates the content (provides only a summary), standard Python libraries (like BeautifulSoup or newspaper3k) can easily extract the full article text using the link provided in the <link> tag of the RSS item, as these sites do not have heavy anti-bot protections.


| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| Good News Network | Uplifting | https://www.goodnewsnetwork.org/feed/ | Positive and inspiring stories daily; frequent updates; no paywalls, focuses on feel-good global news with narrative depth for podcast adaptation. |
| Positive News | Uplifting | https://www.positive.news/feed/ | Independent journalism on positive developments; weekly newsletter but daily feed; uplifting tone, no login required. |
| Reasons to be Cheerful | Community | https://reasonstobecheerful.world/feed/ | Non-profit stories on solutions and community progress; optimistic tone, updated several times a week; free access. |
| Sunny Skyz | Human-interest | https://www.sunnyskyz.com/rss.php | Daily positive news and user-submitted stories; light-hearted tone, high frequency; occasional ads but no gates. |
| Upworthy | Viral | https://www.upworthy.com/rss | Viral stories that inspire and surprise; engaging, shareable content with hooks; daily updates, free. |
| The Dodo | Uplifting | https://www.thedodo.com/rss | Animal rescues and heartwarming stories; quirky and emotional narratives; frequent posts, no paywalls. |
| Bored Panda | Quirky | https://www.boredpanda.com/feed/ | User-generated quirky, viral lists and stories; fun tone, daily; community-driven, may vary in quality. |
| Oddity Central | Quirky | https://www.odditycentral.com/feed | Weird and wonderful human stories; surprising and "wow" moments; updated regularly, free access. |
| UPI Odd News | Quirky | https://www.upi.com/rss/Odd_News/ | Strange and funny news bites; light-hearted, daily; suitable for short hooks with context. |
| Reddit r/UpliftingNews | Uplifting | https://www.reddit.com/r/UpliftingNews/.rss | Community-curated positive stories; viral potential, frequent; user-generated, monitor for consistency. |
| Reddit r/MadeMeSmile | Community | https://www.reddit.com/r/MadeMeSmile/.rss | Wholesome, surprising community acts; uplifting tone, high volume; potential moderation issues but generally positive. |

# Project 4: Content Automation RSS Sources
## TikTok-Style Viral/Human-Interest Content → Paid Podcast Funnel

**Target Audience:** US 18–44, broad appeal  
**Content Theme:** Viral, uplifting, human-interest, "wow" moments

---

## Tier 1: Primary Sources (High Volume, Reliable RSS)

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| **Good News Network** | Uplifting | `https://www.goodnewsnetwork.org/feed/` | Gold standard since 1997. Daily updates, professional editorial. Categories include Heroes, Animals, Inspiring. High narrative depth for podcast expansion. |
| **Upworthy** | Uplifting/Viral | `https://upworthy.com/feeds/feed.rss` | 10M+ Facebook followers. Emotional, shareable stories. Already optimized for viral hooks. Great source for "unlikely hero" angles. |
| **Bored Panda** | Quirky/Viral | `http://feeds.feedburner.com/BoredPanda` | Massive reach (15M FB). Mix of wholesome, funny, "wow" listicles. High image content. 150+ articles/week. Some celebrity gossip to filter. |
| **Reddit r/UpliftingNews** | Human-Interest | `https://www.reddit.com/r/UpliftingNews/.rss` | 18M+ members. Crowd-curated feel-good news. Real-time trending. Source URLs link to original articles for deeper research. |
| **Sunny Skyz** | Uplifting | `https://feeds.feedburner.com/SunnySkyz` | Pure positivity focus. Mix of news, videos, heartwarming stories. Good "rescue" and "community surprise" content. |

---

## Tier 2: High-Quality Niche Sources

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| **Atlas Obscura** | Quirky/Wow | `https://www.atlasobscura.com/feeds/latest` | Strange, wondrous places and stories. Perfect for "did you know" hooks. Well-written, narrative-rich. ~5-10 posts/day. |
| **Reasons to be Cheerful** | Uplifting | `https://reasonstobecheerful.world/feed` | David Byrne's project. Solutions journalism, proven positive stories. Higher editorial quality. Good for podcast depth. |
| **Mental Floss** | Quirky | `https://www.mentalfloss.com/rss.xml` | Trivia, surprising facts, "Big Questions" format. Perfect hook material. Nostalgic 90s/00s content available. |
| **Positive News** | Uplifting | `https://positive.news/feed` | UK-based but global stories. Magazine quality. Longer pieces = more podcast material. |
| **Reddit r/MadeMeSmile** | Human-Interest | `https://www.reddit.com/r/MadeMeSmile/.rss` | 5.3M members. Personal stories + wholesome content. Good user-submitted "everyday hero" stories. |
| **Reddit r/HumansBeingBros** | Community | `https://www.reddit.com/r/HumansBeingBros/.rss` | 3.5M members. Videos/GIFs of people helping each other. Visual-first content, perfect for TikTok adaptation. |

---

## Tier 3: Supplementary Sources

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| **The Optimist Daily** | Uplifting | `https://optimistdaily.com/feed/` | Solutions-focused daily newsletter format. Concise stories. |
| **Good Good Good** | Uplifting | `https://goodgoodgood.co/articles/rss.xml` | Independent positive media. Good mix of news + resources. |
| **UPI Odd News** | Quirky | `https://rss.upi.com/news/odd_news.rss` | Wire service weird news. Short items, daily updates. Reliable but needs verification. |
| **AP Oddities** | Quirky | `https://apnews.com/oddities` (check for RSS) | Associated Press strange news. High credibility. May need RSS generator. |
| **Narratively** | Human-Interest | `https://narratively.com/feed/` | Longform human stories. Fewer posts but very high quality. Excellent for podcast deep-dives. |
| **Oddity Central** | Quirky | `https://www.odditycentral.com/feed/` | Weird news from around the world. Active updates. Strange but true stories. |

---

## Tier 4: Animal-Focused Sources

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| **The Dodo** | Animal/Uplifting | `https://www.thedodo.com/rss` (verify) | #1 animal brand on social. Highly viral rescue stories. May need RSS.app generator if native feed unavailable. |
| **The Animal Rescue Site** | Animal/Community | `https://theanimalrescuesite.com/blog/feed` | Rescue stories, adoption news. Lower volume but high quality. |
| **World Animal News** | Animal | `https://worldanimalnews.com/feed/` | Advocacy-focused animal welfare news. |
| **Bored Panda (Animals)** | Animal/Quirky | `https://www.boredpanda.com/category/animals/feed/` | Category-specific feed for animal content only. |

---

## Content Type Matrix

| Content Type | Best Sources | Hook Potential | Podcast Depth |
|--------------|--------------|----------------|---------------|
| **Unlikely Heroes** | GNN, Upworthy, r/UpliftingNews | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Animal Rescues** | The Dodo, Bored Panda, GNN | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Community Surprises** | r/MadeMeSmile, Sunny Skyz, r/HumansBeingBros | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Quirky/Wow Facts** | Atlas Obscura, Mental Floss, Oddity Central | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Feel-Good Outcomes** | Reasons to be Cheerful, Positive News | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Viral Moments** | Bored Panda, Reddit subs, Upworthy | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## Technical Notes

### RSS Feed Patterns
- **WordPress sites:** Usually `/feed/` or `/rss/`
- **Reddit:** `https://www.reddit.com/r/{subreddit}/.rss` or `.json`
- **Custom:** May require RSS.app or similar generator

### Recommended Scraping Approach
1. Poll Tier 1 sources every 15-30 minutes
2. Poll Tier 2-3 sources every 1-2 hours
3. Filter by keywords: "hero", "rescue", "surprise", "community", "viral", "heartwarming"
4. Deduplicate by URL and story similarity
5. Score by engagement metrics if available (Reddit upvotes, etc.)

### Content Filtering Suggestions
**Include:** Rescues, reunions, community fundraising, random acts of kindness, medical recoveries, animal stories, "against all odds" narratives, record-breaking achievements, wholesome viral moments

**Exclude:** Political, overly tragic (even with positive spin), controversial social issues, celebrity gossip, promotional/sponsored content

---

## Quick-Start Feed Bundle (Copy-Paste Ready)

```
https://www.goodnewsnetwork.org/feed/
https://upworthy.com/feeds/feed.rss
http://feeds.feedburner.com/BoredPanda
https://www.reddit.com/r/UpliftingNews/.rss
https://www.reddit.com/r/MadeMeSmile/.rss
https://feeds.feedburner.com/SunnySkyz
https://www.atlasobscura.com/feeds/latest
https://reasonstobecheerful.world/feed
https://positive.news/feed
https://www.mentalfloss.com/rss.xml
```

Here are **active, non-paywalled RSS sources** that reliably produce **uplifting / viral / human-interest** stories with enough context to expand into a **7–10 minute** podcast segment.

| Source Name                                      | Category       | Feed URL                                                                                       | Notes (tone, frequency, any issues)                                                                                                                      |
| ------------------------------------------------ | -------------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Positive News                                    | Uplifting      | [https://www.positive.news/feed/](https://www.positive.news/feed/)                             | “Constructive / hopeful” journalism; steady cadence; great for “the world isn’t doomed” hooks. ([RSS Database - FeedSpot][1])                            |
| Good News Network                                | Uplifting      | [https://www.goodnewsnetwork.org/feed/](https://www.goodnewsnetwork.org/feed/)                 | High volume of feel-good wins, rescues, breakthroughs; very “clip-able” headlines. ([RSS Database - FeedSpot][1])                                        |
| The Optimist Daily                               | Uplifting      | [https://optimistdaily.com/feed](https://optimistdaily.com/feed)                               | Daily “solutions + good news” mix; often has clear “problem → fix → impact” arc. ([RSS Database - FeedSpot][1])                                          |
| Sunny Skyz                                       | Viral          | [https://feeds.feedburner.com/SunnySkyz](https://feeds.feedburner.com/SunnySkyz)               | Fast-moving “make you smile” viral stories; great for short hooks; sometimes lighter sourcing (worth quick verification). ([RSS Database - FeedSpot][2]) |
| Not All News Is Bad!                             | Human-interest | [https://notallnewsisbad.com/feed/](https://notallnewsisbad.com/feed/)                         | Curated “antidote” vibe; strong community/kindness stories; usually 1/day style (easy pipeline). ([Not All News is Bad!][3])                             |
| SA Good News                                     | Community      | [https://www.sagoodnews.co.za/feed/](https://www.sagoodnews.co.za/feed/)                       | Community progress + uplifting local impact stories (South Africa focus); good “restoring faith” narratives. ([The Home Of Great South African News][4]) |
| UPI Odd News                                     | Quirky         | [https://rss.upi.com/news/odd_news.rss](https://rss.upi.com/news/odd_news.rss)                 | Quirky + weird + “how is this real?”; great for “wow” openers; generally short, punchy writes. ([RSS Database - FeedSpot][5])                            |
| Bored Panda (Listicles)                          | Viral          | [https://www.boredpanda.com/listicles-feed/](https://www.boredpanda.com/listicles-feed/)       | High-volume viral packaging; excellent hook factory; you’ll want dedupe + quality filters. ([Straight from the Horse's Heart][6])                        |
| Bored Panda (Site feed)                          | Viral          | [https://2.boredpanda.com/feed](https://2.boredpanda.com/feed)                                 | Broader firehose vs listicles-only; good as a secondary feed with stronger filtering. ([nileharvest][7])                                                 |
| Laughing Squid (main)                            | Quirky         | [http://feeds.laughingsquid.com/laughingsquid](http://feeds.laughingsquid.com/laughingsquid)   | Internet oddities + clever human stories; often highly “TikTok captionable.” ([RSS Database - FeedSpot][2])                                              |
| Laughing Squid (SquidList)                       | Quirky         | [http://feeds.laughingsquid.com/squidlist](http://feeds.laughingsquid.com/squidlist)           | Similar tone, sometimes more link-roundup style; best when paired with a “must include narrative” rule. ([RSS Database - FeedSpot][2])                   |
| Atlas Obscura (Latest)                           | Quirky         | [https://www.atlasobscura.com/feeds/latest.xml](https://www.atlasobscura.com/feeds/latest.xml) | “Strange & wondrous places/people” = instant “wow”; strong context for longer segments. ([GitHub][8])                                                    |
| This Is Colossal                                 | Human-interest | [https://www.thisiscolossal.com/feed/](https://www.thisiscolossal.com/feed/)                   | Visual “awe” stories (art/nature/craft/humans); great for wonder/curiosity angles. ([RSS Database - FeedSpot][9])                                        |
| Jane Goodall “Good for All News” (RSS directory) | Community      | [https://news.janegoodall.org/rss-feeds/](https://news.janegoodall.org/rss-feeds/)             | Central page listing multiple RSS options; strong “hope in action” conservation/community stories. ([Jane Goodall's Good for All News][10])              |

**Quick automation tips (so these stay “viral” and podcast-ready):**

* Add a **“narrative completeness” filter**: prefer items that contain *who/what/where + stakes + payoff* in the first ~2 paragraphs.
* Add **dedupe rules** (especially for Bored Panda / Sunny Skyz): normalize by canonical URL + story title similarity.
* Add a **verification step** for the more viral/aggregator-leaning sources (e.g., if a post cites another outlet, scrape that original too).

If you want, I can also propose a **scoring rubric** (Hook score / Emotional lift / Narrative depth / Verifiability) you can drop directly into your pipeline.

[1]: https://rss.feedspot.com/good_news_rss_feeds/ "35 Best Good News RSS Feeds"
[2]: https://rss.feedspot.com/good_news_rss_feeds/?utm_source=chatgpt.com "35 Best Good News RSS Feeds"
[3]: https://notallnewsisbad.com/about/?utm_source=chatgpt.com "About"
[4]: https://www.sagoodnews.co.za/rss-feeds/ "RSS Feeds | The Home Of Great South African News | SA Good News"
[5]: https://rss.feedspot.com/upi_rss_feeds/?utm_source=chatgpt.com "Top 15 UPI RSS Feeds"
[6]: https://rtfitchauthor.com/tag/the-dodo/?utm_source=chatgpt.com "The Dodo - Straight from the Horse's Heart"
[7]: https://nileharvest.us/top-10-upi-rss-feeds/?utm_source=chatgpt.com "Top 10 UPI RSS Feeds - Nile Harvest | nileharvest"
[8]: https://github.com/plenaryapp/awesome-rss-feeds?utm_source=chatgpt.com "plenaryapp/awesome-rss-feeds"
[9]: https://rss.feedspot.com/art_rss_feeds/?utm_source=chatgpt.com "Top 100 Art RSS Feeds"
[10]: https://news.janegoodall.org/rss-feeds/?utm_source=chatgpt.com "RSS Feeds - Jane Goodall's Good for All News"
