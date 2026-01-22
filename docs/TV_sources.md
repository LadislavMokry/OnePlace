Here are high-quality, scrape-friendly sources tailored for a US Millennial audience focused on TV and Streaming. These sources have been selected for their active RSS feeds, lack of hard paywalls, and specific focus on narrative recaps, endings, and streaming culture rather than general celebrity gossip.

Recommended Source List
Source Name	Category	Feed URL	Notes
TVLine	Recaps & Renewals	https://tvline.com/feed/	Gold standard. High volume of recaps, "Renewal/Cancellation Scorecards," and spoiler-heavy scoops. Perfect for "Did your show get cancelled?" hooks.
Decider	Streaming News & Calendar	https://decider.com/feed/	High Utility. Focuses heavily on "What to Watch This Weekend" and "New on Netflix/Hulu." Tone is casual and decisive ("Stream It or Skip It").
ScreenRant (TV Only)	Explainers & Endings	https://screenrant.com/feed/tv/	Content Farm Style. Excellent for automation because they use structured headers (e.g., "Season 4 Ending Explained"). High volume of "Easter Eggs" and "Hidden Details."
Collider (TV Only)	Streaming News & Deep Dives	https://collider.com/feed/tv/	Great for "What We Know So Far" guides regarding upcoming seasons. Good balance of news and enthusiastic opinion pieces.
Den of Geek	Recaps (Genre Focus)	https://www.denofgeek.com/tv/feed/	Niche Appeal. Essential for Sci-Fi/Fantasy hits (House of the Dragon, The Boys, Marvel/Star Wars). Millennials skew heavily toward these genres.
CinemaBlend (TV)	Buzz & Viral Moments	https://www.cinemablend.com/feeds/tv	Focuses on audience reactions and viral moments within episodes. Good for finding the specific "scene everyone is talking about."
TV Insider	Release Calendar & Previews	https://www.tvinsider.com/feed/	Associated with TV Guide but more modern. concise episode descriptions and reliable release date info. Good for the "Coming up next week" segment.
SlashFilm (/Film)	Reviews & Critical Analysis	https://www.slashfilm.com/feed/category/tv/	Slightly more analytical but very pop-culture literate. Good for scripting the "Why this show matters" portion of the podcast.
ComingSoon.net	Release Dates	https://www.comingsoon.net/feed	Utility. While they cover movies, their TV news is strictly factual—trailers, release dates, and casting. Easy to parse for calendar data.
Bleeding Cool	Recaps & Spoilers	https://bleedingcool.com/tv/feed/	Very casual, blog-style voice. They cover a lot of British exports (Doctor Who) and comic-book shows popular with this demographic.
Implementation Tips for Automation

Filtering Logic: Since you want to avoid "Celebrity Gossip," set your scraper to exclude articles containing keywords like Red Carpet, Outfit, Dating, Divorce, or Rumor in the title. Focus on keywords like Recap, Review, Ending, Season [X], Trailer, and Premiere.

Spoiler Extraction: Sources like ScreenRant and CBR often put "Spoiler" in the title or use a specific HTML tag for spoiler blocks. If parsing HTML, look for Warning: Spoilers text to automatically insert your required audio disclaimer.

Visuals for TikTok: Sources like TVLine and Collider usually include high-res featured images in their RSS <media:content> or <enclosure> tags. These are essential for the visual component of your TikTok hooks.

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| Decider | Recaps | https://decider.com/feed/ | Engaging and hook-oriented tone suitable for short-form content; daily updates with narrative recaps and episode breakdowns; no paywalls or issues, focuses on streaming shows with spoilers. |
| SpoilerTV | Recaps | https://www.spoilertv.com/feeds/posts/default | Analytical tone with community discussions and polls; multiple updates per day including episode reviews; active and free, ideal for narrative context in podcasts; includes spoiler warnings. |
| TVLine | Streaming News | https://tvline.com/feed/ | Fun, buzz-focused tone on renewals, cancellations, and viewership; frequent daily posts; high-quality TV-centric content without paywalls, good for major twists and release buzz. |
| What's on Netflix | Release Calendar | https://www.whats-on-netflix.com/feed/ | Informative and promotional tone; hourly updates on new releases and calendars; Netflix-specific but broad coverage of recaps and news; no issues, suitable for automated scraping. |
| TV Series Finale | Streaming News | https://tvseriesfinale.com/feed/ | Informational tone on ratings and viewership buzz; weekly updates including renewals/cancellations; no paywalls, provides data for podcast segments on show performance. |
| JustWatch | Release Calendar | https://openrss.org/www.justwatch.com/us/new/tv-shows | Neutral, data-driven tone; updates as new releases occur; covers new TV episodes and seasons across platforms; free and active, customizable via filters for broader or specific scraping. |
| ShowRSS | Release Calendar | https://showrss.info/browse | Customizable tone based on selected shows; daily episode release updates; free RSS generation for TV show air dates and episodes; no paywalls, focuses on release schedules without gossip. |
| Cinemablend | Reviews/Explainers | https://www.cinemablend.com/rss/topic/news/television | Engaging and explanatory tone; frequent updates on endings, twists, and analyses; TV-focused without paywalls, good for deeper narrative hooks. |

# Project 2: TV & Streaming Recaps - RSS Source List

**Goal:** Short-form TikTok-style content → Drive to paid daily podcast (7–10 min)  
**Audience:** US/English-speaking millennials (25–40)  
**Theme:** TV & Streaming Recaps (episode recaps, season summaries, ending explanations, renewals/cancellations, release dates, viewership buzz, major twists)

---

## Verified Working RSS Feeds

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| **TVLine** | Recaps, News, Spoilers | `https://tvline.com/feed/` | ✅ VERIFIED. Hourly updates. Gold standard for TV recaps, casting news, spoilers. Excellent hook material with cliffhangers and reveals. High frequency. |
| **TV Series Finale** | Renewals/Cancellations | `https://tvseriesfinale.com/feed/` | ✅ VERIFIED. Dedicated to cancelled/renewed show tracking. Perfect for "will your show survive?" hooks. Referenced by major outlets (NYT, LA Times). |
| **TV Insider** | Recaps, Reviews | `https://tvinsider.com/feed/` | ✅ VERIFIED. Comprehensive TV coverage, episode previews, behind-the-scenes. Good for "what to watch" content. |
| **Den of Geek** | Explainers, Reviews | `https://denofgeek.com/feed/` | ✅ VERIFIED. Deep dives on genre TV (sci-fi, fantasy, horror). Great for ending explanations and theory content. US/UK audience. |
| **The Wrap** | Streaming News | `https://thewrap.com/feed/` | ✅ VERIFIED. Industry-focused streaming news, viewership data, platform wars. Good for "Netflix vs Disney+" narrative hooks. |
| **IndieWire** | Reviews, Industry | `https://indiewire.com/feed/rss` | Prestige TV coverage, awards season, in-depth reviews. Higher-brow content for quality hooks. |
| **CinemaBlend TV** | Recaps, News | `https://www.cinemablend.com/television/rss.xml` | Full TV section feed. Accessible pop-culture tone, good for casual millennial audience. |
| **SpoilerTV** | Spoilers, Recaps | `https://spoilertv.com/feeds/posts/default` | Massive spoiler database. Show-specific feeds available. Ideal for "what happens next" hooks. |
| **Entertainment Weekly TV** | Recaps, Reviews | `https://feeds-api.dotdashmeredith.com/rss/ew/tv` | Legacy brand, episode recaps, exclusive interviews. Trusted source for mainstream audience. |
| **Slant Magazine TV** | Reviews, Recaps | `https://slantmagazine.com/category/tv/feed/` | Thoughtful reviews and recaps with critical perspective. Good for "was this episode actually good?" angles. |

---

## Streaming-Specific Sources

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| **What's on Netflix** | Release Calendar, News | `https://www.whats-on-netflix.com/feed/` | Netflix-focused: new releases, leaving soon, original series news. Perfect for "dropping this week" content. |
| **What's on Netflix - Leaving Soon** | Release Calendar | `https://www.whats-on-netflix.com/leaving-soon/feed/` | Urgency hooks: "Watch before it's gone!" content. |
| **NewOnNetflix USA** | Release Calendar | `https://usa.newonnetflix.info/feed` | Daily additions tracker. Straightforward new release alerts. |

---

## Supplementary Sources (May Require RSS Generator)

These sources have excellent content but their native RSS may need verification or generation via RSS.app:

| Source Name | Category | Website | Notes |
|-------------|----------|---------|-------|
| **Decider** | Streaming Guide | decider.com | "What to watch" focus. Platform-specific guides (Netflix, Disney+, Hulu, Max). May need RSS.app to generate feed. |
| **Vulture TV** | Recaps, Analysis | vulture.com/tv | Smart, witty coverage from NY Magazine. Excellent recap quality. Try RSS.app for section feed. |
| **Collider** | News, Trailers | collider.com | Movie/TV news with strong trailer coverage. Native feed may be unstable. |
| **Screen Rant TV** | News, Explainers | screenrant.com/tv | High volume, SEO-optimized content. Good for trending topics. |
| **A.V. Club TV** | Reviews, Recaps | avclub.com/tv | Pop culture obsessives. Quality recaps with humor. Now under Paste Media. |

---

## Content Strategy Notes

### Best for Short-Form Hooks
1. **TVLine** - Breaking casting news, spoiler reveals, cliffhanger discussions
2. **TV Series Finale** - Cancellation/renewal drama creates urgency
3. **SpoilerTV** - "Here's what happens..." teasers
4. **What's on Netflix - Leaving Soon** - FOMO-driven "watch before gone" hooks

### Best for Podcast Deep-Dives (7–10 min)
1. **Den of Geek** - Detailed explainers provide podcast backbone
2. **Vulture** - Smart analysis translates to engaging discussion
3. **IndieWire** - Awards/prestige content for quality-focused segments
4. **A.V. Club** - Cultural context and humor for engaging narration

### Release Calendar Priority
- **What's on Netflix** (Netflix drops)
- **TV Insider** (Network premieres)
- **Decider** (Multi-platform overview)

---

## Spoiler Warning Template

Per project requirements, all recap content should include:

> ⚠️ **SPOILER WARNING** ⚠️  
> This [video/episode] contains spoilers for [SHOW NAME] [Season X/Episode X].

---

## Feed Maintenance Notes

- Verify feeds quarterly - URLs can change
- Monitor for paywall additions (especially Deadline, Variety)
- Consider RSS.app ($9/mo) for generating feeds from sites without native RSS
- SpoilerTV offers show-specific feeds - useful for trending series coverage

---

| Source Name          | Category           | Feed URL                                                                                                       | Notes (tone, frequency, any issues)                                                                                                          |
| -------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| TVLine               | Recaps             | [https://tvline.com/feed](https://tvline.com/feed)                                                             | Fast-moving TV coverage with a lot of episode/season coverage + renewals/cancellations; good headline hooks. ([RSS Database - FeedSpot][1])  |
| Tell-Tale TV         | Recaps             | [https://telltaletv.com/feed](https://telltaletv.com/feed)                                                     | Episodic reviews/recaps + previews; solid narrative context for 7–10 min podcast segments. ([RSS Database - FeedSpot][1])                    |
| Ready Steady Cut     | Recaps             | [https://readysteadycut.com/feed](https://readysteadycut.com/feed)                                             | Heavy on streaming recaps + “ending explained”-style pieces; very TikTok-hookable headlines. ([RSS Database - FeedSpot][2])                  |
| TV Show Pilot        | Recaps             | [https://tvshowpilot.com/feed](https://tvshowpilot.com/feed)                                                   | Recap/review-driven site; useful for quick story summaries and “what happened” beats. ([RSS Database - FeedSpot][3])                         |
| Digital Spy (TV)     | Streaming News     | [https://www.digitalspy.com/rss/tv.xml](https://www.digitalspy.com/rss/tv.xml)                                 | High volume TV/streaming coverage (UK-based but very relevant to US streaming); good for release chatter. ([RSS Database - FeedSpot][3])     |
| Decider              | Streaming News     | [https://decider.com/feed](https://decider.com/feed)                                                           | “What to watch” + streaming recommendations/news; great for short-form “watch this / skip this” hooks. ([RSS Database - FeedSpot][3])        |
| What’s on Netflix    | Release Calendar   | [https://www.whats-on-netflix.com/feed](https://www.whats-on-netflix.com/feed)                                 | Strong for “new on Netflix,” removals, and release-date posts; very automation-friendly. ([RSS Database - FeedSpot][3])                      |
| TV Insider           | Streaming News     | [https://www.tvinsider.com/feed](https://www.tvinsider.com/feed)                                               | Broad TV coverage (interviews, news, schedules); good mainstream tone for millennials. ([RSS Database - FeedSpot][3])                        |
| IndieWire            | Reviews/Explainers | [https://www.indiewire.com/feed/rss](https://www.indiewire.com/feed/rss)                                       | More “industry + prestige TV” angle; good for explainers/analysis (slightly more serious, still accessible). ([RSS Database - FeedSpot][1])  |
| Give Me My Remote    | Streaming News     | [https://givememyremote.com/remote/feed](https://givememyremote.com/remote/feed)                               | TV blog style; news + exclusives; useful for ongoing show updates (keep show-focused to avoid celeb overlap). ([RSS Database - FeedSpot][3]) |
| SpoilerTV            | Recaps             | [https://www.spoilertv.com/feeds/posts/default?alt=rss](https://www.spoilertv.com/feeds/posts/default?alt=rss) | Spoilers and episode intel; great for twist-driven hooks (label spoiler warnings clearly). ([spoiler275.rssing.com][4])                      |
| TV Series Finale     | Streaming News     | [https://tvseriesfinale.com/feed/](https://tvseriesfinale.com/feed/)                                           | Renewals/cancellations + ratings angle; good “is it coming back?” segments. ([RSS.app][5])                                                   |
| The Futon Critic     | Release Calendar   | [http://www.thefutoncritic.com/rss/news.aspx](http://www.thefutoncritic.com/rss/news.aspx)                     | Press releases + premiere/renewal announcements; excellent for date-driven automation. ([elDiario.es][6])                                    |
| Is My Show Cancelled | Release Calendar   | [https://www.ismyshowcancelled.com/feed/news](https://www.ismyshowcancelled.com/feed/news)                     | Renewals/cancellations + premiere-date updates; simple, feed-first structure. ([RSS Database - FeedSpot][3])                                 |
| TV Is My Pacifier    | Release Calendar   | [https://tvismypacifier.com/feed](https://tvismypacifier.com/feed)                                             | Useful for weekly schedules/what’s on tonight style posts; good for “watch tonight” shorts. ([RSS Database - FeedSpot][3])                   |
| TV Guide Magazine    | Release Calendar   | [https://tvguidemagazine.com/feed](https://tvguidemagazine.com/feed)                                           | “What to watch” positioning; mainstream and generally non-paywalled feed content. ([RSS Database - FeedSpot][3])                             |
| TV Worth Watching    | Release Calendar   | [https://www.tvworthwatching.com/Feed.aspx](https://www.tvworthwatching.com/Feed.aspx)                         | Curated “worth watching” picks + schedule context; good for daily “top picks” episodes. ([RSS Database - FeedSpot][3])                       |

If you want, I can also format these into an **OPML** bundle (so you can import everything into Feedly/Inoreader/n8n) and add a **standard “⚠️ Spoiler warning” template** you can prepend automatically based on the category.

[1]: https://rss.feedspot.com/web_series_rss_feeds/ "Top 20 Web Series RSS Feeds"
[2]: https://rss.feedspot.com/netflix_rss_feeds/?utm_source=chatgpt.com "Top 20 Netflix RSS Feeds"
[3]: https://rss.feedspot.com/tv_rss_feeds/ "Top 80 TV RSS Feeds"
[4]: https://spoiler275.rssing.com/chan-7150393/all_p2262.html?utm_source=chatgpt.com "May 16, 2019, 8:05 pm - SpoilerTV"
[5]: https://rss.app/?utm_source=chatgpt.com "RSS Feed Generator, Create RSS feeds from URL"
[6]: https://www.eldiario.es/vertele/videos/actualidad/the-futon-critic_1_7720640.html?utm_source=chatgpt.com "The Futon Critic"
