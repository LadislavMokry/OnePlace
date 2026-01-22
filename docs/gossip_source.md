
Here is a curated list of high-quality, active RSS feeds suitable for a content automation system targeting US Millennials.
These sources have been selected because they provide the "Hook" (sensational headlines for TikTok) and the "Substance" (narrative details, timelines, and quotes) necessary to script a 7–10 minute podcast segment. They avoid episode recaps and focus on the personalities and business of entertainment.
Project 1: Celebrity & Entertainment News Feeds
Source Name	Category	Feed URL	Notes
TMZ	Celebrity Gossip / Scandals	https://www.tmz.com/rss.xml	Essential. The fastest source for breaking scandals, arrests, and deaths. Excellent for "Breaking News" TikTok hooks. Note: Very high frequency; scraping logic should filter by "Exclusive" tags to avoid fluff.
Page Six	Society / PR Drama	https://pagesix.com/feed/	High Value. Focuses on NYC high society, celebrity relationships, and PR leaks. The tone is snarky and perfect for Millennial commentary. Great for deep dives into why a celeb is doing a paparazzi walk.
People Magazine	Official News / Red Carpet	https://people.com/feed/	The "Record of Truth." While less edgy, this is where celebs go to confirm divorces or births. Use this to verify facts for the podcast segment against the rumors from TMZ.
BuzzFeed (Celebrity)	Pop Culture / Nostalgia	https://www.buzzfeed.com/celebrity.xml	Target Audience Match. Heavily focused on Millennials (25-40). Covers internet reactions, Twitter/X drama, and 2000s nostalgia. Excellent for "Did you see what the internet is saying about X?" hooks.
Deadline	Industry News / Casting	https://deadline.com/feed/	Industry "Inside Baseball." Focuses on casting shakeups, movie cancellations, and strikes. Use this for the "Business of Hollywood" segments (e.g., "Why this movie got cancelled"). Warning: Filter out "Box Office" reports.
Just Jared	Red Carpet / Sightings	http://www.justjared.com/feed/	Visual/Status. Focuses on who was seen with whom and what they wore. Articles are often short, but the headlines provide great "spotted" content for visual TikToks.
Radar Online	Scandals / Legal Drama	https://radaronline.com/feed/	Gritty/Tabloid. Digs deep into court documents, lawsuits, and family feuds. Provides the specific legal details needed to flesh out a 10-minute podcast episode on a celebrity trial.
Uproxx (Music)	Music / Hip-Hop Culture	https://uproxx.com/music/feed/	Music News. Covers beefs, album rollouts, and artist controversies. Good for separating general celebrity gossip from specific music industry headlines.
Daily Mail (Showbiz)	Global Gossip	https://www.dailymail.co.uk/tvshowbiz/index.rss	Volume. Extremely high output. The headlines are famously descriptive (paragraph-long), which actually helps AI summarize the "hook" easily. Warning: British spelling/slang may need normalization for US audience.
Cheat Sheet (Ent.)	Entertainment Deep Dives	https://www.cheatsheet.com/entertainment/feed/	Narrative. often does "Retrospectives" or "The truth about..." articles. Useful for sourcing background info to pad out the podcast length.
Implementation Tips for Automation
Filtering "Recaps":
Even though these sources are generally news-focused, Deadline and Uproxx may occasionally post episode reviews. In your scraper logic, exclude items containing keywords like: "Recap," "Review," "Season [X] Episode [Y]," or "Ending Explained."
The "Hook" vs. The "Meat":
Use TMZ and Page Six to generate the TikTok script (the "What happened").
Use People and Deadline to generate the Podcast script (the "Context, confirmations, and industry impact").
Image Scraping:
Just Jared and Daily Mail are image-heavy. If your automation pulls assets for the TikTok video background, these two feeds are the most reliable for high-resolution celebrity candid shots.


| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| TMZ | Celebrity Gossip | https://www.tmz.com/rss.xml | Sensational tone, fast-moving updates multiple times a day, no paywall or issues, great for hooks on scandals and headlines. |
| Page Six | Celebrity Gossip | https://pagesix.com/gossip/feed/ | Snarky, insider gossip style, frequent posts, free access, suitable for PR drama and relationships. |
| Us Weekly | Celebrity Gossip | https://www.usmagazine.com/category/celebrity-news/feed/ | Light-hearted and engaging tone, daily updates, no paywall, good narrative for podcast segments. |
| Just Jared | Red Carpet | https://www.justjared.com/feed/ | Event-focused with photo emphasis, high frequency, free, ideal for red-carpet moments and celebrity sightings. |
| Perez Hilton | Celebrity Gossip | https://perezhilton.com/feed/ | Opinionated and personal gossip, medium frequency, no issues, provides context for scandals. |
| The Shade Room | Celebrity Gossip | https://theshaderoom.com/feed/ | Urban and pop culture gossip, very frequent updates, free, engaging for millennial audience. |
| Hollywood Life | Culture | https://hollywoodlife.com/feed/ | Entertainment and lifestyle mix, high frequency, no paywall, good for pop-culture headlines. |
| Variety | Industry News | https://variety.com/feed/ | Professional yet entertaining tone, daily updates, some articles may be paywalled but RSS summaries are free, focuses on industry shakeups. |
| Deadline | Industry News | https://deadline.com/feed/ | Breaking news style, high frequency, fully free, excellent for casting news and entertainment business drama. |
| Billboard | Music | https://www.billboard.com/feed/ | Pop music headlines, daily updates, no issues, suitable for music-related celebrity news. |
| Rolling Stone | Music | https://www.rollingstone.com/music/feed/ | Cultural music insights, frequent posts, some paywalled content but good for hooks, avoids serious academic tone. |
| BuzzFeed Celebrity | Culture | https://www.buzzfeed.com/celebrity.xml | Fun, viral content, high frequency, free, great for short-form hooks and relatable narratives. |
| POPSUGAR | Culture | https://www.popsugar.com/rss | Lifestyle and celeb mix, daily updates, no paywall, provides narrative context for relationships and trends. |

# Project 1: Celebrity/Entertainment RSS Sources

## Overview
Curated RSS feeds for automated content scraping - targeting TikTok-style hooks driving traffic to a daily podcast (7-10 min). Audience: US/English-speaking millennials (25-40).

---

## Primary Sources Table

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| **TMZ** | Celebrity Gossip | `https://www.tmz.com/rss.xml` | ⭐ Fast-breaking gossip, high volume (50+ posts/day), perfect hook material, sassy tone. The gold standard for celeb drama. |
| **Page Six** | Celebrity Gossip | `https://pagesix.com/feed/` | ⭐ NY Post's gossip arm, insider scoops, relationship drama, PR feuds. Great narrative hooks. |
| **Us Weekly** | Celebrity Gossip | `https://usmagazine.com/feed/` | Relationship-heavy, "who's dating who," celebrity lifestyle. Ideal for millennial nostalgia angles. |
| **Just Jared** | Celebrity Gossip | `https://justjared.com/feed/` | High-volume photo-driven content, red carpet, street style, celeb sightings. Good visual hooks. |
| **Perez Hilton** | Celebrity Gossip | `https://perezhilton.com/feed/` | OG gossip blog, snarky tone, reality TV heavy. Strong voice for podcast adaptation. |
| **Hollywood Life** | Celebrity Gossip | `https://hollywoodlife.com/feed/` | Mix of gossip + lifestyle, relationship updates, fashion moments. Good depth for podcast segments. |
| **The Shade Room** | Celebrity Gossip | `https://theshaderoom.com/feed/` | ⭐ Massive social engagement, hip-hop/R&B celeb focus, viral-ready content. 29M Instagram followers validate hook potential. |
| **E! Online** | Celebrity News | `https://eonline.com/rss/` | Mainstream celebrity coverage, red carpet, awards shows. Reliable but less edgy. |
| **Entertainment Tonight** | Celebrity News | `https://etonline.com/news/rss` | Authoritative celebrity interviews, premiere coverage. Good for "behind the scenes" angles. |
| **Extra TV** | Celebrity News | `https://feeds.extratv.com/rss` | Celebrity interviews, premiere coverage, lifestyle content. Solid mainstream source. |

---

## Industry News Sources

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| **Variety** | Industry News | `https://variety.com/feed/` | ⭐ Casting news, deal announcements, industry shakeups. Great for "breaking" hooks about upcoming projects. |
| **Deadline** | Industry News | `https://deadline.com/feed/` | ⭐ First to break casting/deal news. Essential for industry scoops that become mainstream gossip. |
| **The Hollywood Reporter** | Industry News | `https://hollywoodreporter.com/feed/` | In-depth industry coverage, exec moves, awards race. Good for deeper podcast context. |
| **IndieWire** | Industry News | `https://indiewire.com/feed/` | Film/TV industry news, festival coverage. Useful for prestige content hooks. |

---

## Music & Pop Culture Sources

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| **Billboard** | Music | `https://billboard.com/feed/` | ⭐ Chart news, artist updates, music industry drama. Perfect for "who's #1" hooks. |
| **Rolling Stone** | Music/Culture | `https://rollingstone.com/music/feed/` | Music news + broader culture. Good narrative depth for podcast segments. |
| **The Hollywood Gossip** | Culture | `https://thehollywoodgossip.com/feed/` | Scandals, reality TV, relationship drama. High volume gossip aggregator. |

---

## Red Carpet & Style Focus

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| **Wonderwall** | Red Carpet | `https://wonderwall.com/feed/` | Photo-heavy celebrity coverage, fashion moments, red carpet breakdowns. Visual hook potential. |
| **OK! Magazine** | Red Carpet/Gossip | `https://okmagazine.com/rss` | Celebrity style, relationship news, royal coverage. Tabloid tone works for hooks. |

---

## Supplementary Sources

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| **Daily Mail US Showbiz** | Celebrity Gossip | `https://dailymail.co.uk/usshowbiz/index.rss` | Extremely high volume, paparazzi-heavy, sensational headlines. Good for viral angles but verify accuracy. |
| **Nicki Swift** | Celebrity Gossip | `https://nickiswift.com/feed/` | Explainer-style celebrity content, good for "the untold truth" angles. |
| **AceShowbiz** | Celebrity News | `https://aceshowbiz.com/rsspage/news.xml` | Aggregated celebrity news, decent volume, straightforward coverage. |
| **BuzzFeed Celebrity** | Culture | `https://buzzfeed.com/celebrity.xml` | Pop culture commentary, listicles, social media reactions. Good millennial engagement angles. |

---

## Recommended Priority Tiers

### Tier 1 (Must-Have for Daily Scraping)
1. **TMZ** - Breaking gossip, highest volume
2. **Page Six** - Insider scoops, relationship drama  
3. **The Shade Room** - Viral potential, high engagement
4. **Deadline** - Industry breaking news
5. **Billboard** - Music news hooks

### Tier 2 (Daily Supplement)
6. Us Weekly
7. Just Jared
8. Hollywood Life
9. Variety
10. Entertainment Tonight

### Tier 3 (Weekly Deep Dives)
11. Hollywood Reporter
12. Rolling Stone
13. Perez Hilton
14. E! Online

---

## Technical Notes

1. **Feed Validation**: All URLs should be tested before production. Some may redirect or require specific headers.

2. **Rate Limiting**: TMZ and Daily Mail have high volumes - consider filtering by engagement metrics or keywords.

3. **Content Overlap**: Many sources cover the same stories - implement deduplication logic based on celebrity names + date.

4. **Paywall Warning**: Hollywood Reporter and Variety have partial paywalls on full articles - RSS feeds typically show summaries.

5. **Image Rights**: Most feeds include image URLs but usage rights vary - generate original visuals for TikTok content.

---

## Keyword Filters for Relevance

To avoid TV recap content (your other project), filter OUT these terms:
- "episode recap"
- "season finale"
- "premiere review"
- "what happened on"
- "spoiler"

Filter IN these high-engagement terms:
- "dating"
- "split"
- "divorce"
- "feud"
- "claps back"
- "spotted"
- "red carpet"
- "breakup"
- "engaged"
- "pregnant"
- "scandal"
- "drama"

---

Here are **active, high-signal, scrape-friendly RSS/Atom sources** for US/English celebrity & entertainment headlines (mix of fast gossip + industry/trade + music + red-carpet/style). All URLs below are **direct feeds**.

| Source Name                           | Category         | Feed URL                                                                                                                                             | Notes                                                                                                                                                  |
| ------------------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| TMZ                                   | Celebrity Gossip | [http://www.tmz.com/rss.xml](http://www.tmz.com/rss.xml)                                                                                             | Fast-moving exclusives + scandal/relationship beats; great hook density. ([About Facebook][1])                                                         |
| People – Celebrity                    | Celebrity Gossip | [https://feeds-api.dotdashmeredith.com/v1/rss/people/celebrity](https://feeds-api.dotdashmeredith.com/v1/rss/people/celebrity)                       | Cleaner “celebrity” slice (less broad lifestyle). Strong narrative context for 7–10 min segments.                                                      |
| Us Weekly (Atom)                      | Celebrity Gossip | [http://www.usmagazine.com/feeds/movies_tv_music/atom](http://www.usmagazine.com/feeds/movies_tv_music/atom)                                         | High-frequency celeb relationship/news cycles; very “podcastable.” ([About Facebook][1])                                                               |
| Celebitchy (RSS2)                     | Celebrity Gossip | [https://www.celebitchy.com/feed/rss2/](https://www.celebitchy.com/feed/rss2/)                                                                       | Opinionated voice; strong for “hot take + why this matters.” (Contains royals/politics sometimes—filter by topic tags/keywords.) ([celebitchy.com][2]) |
| E! Online – Top Stories               | Celebrity Gossip | [http://syndication.eonline.com/syndication/feeds/rssfeeds/topstories.xml](http://syndication.eonline.com/syndication/feeds/rssfeeds/topstories.xml) | Mainstream celeb pipeline (relationships, PR drama, red carpet). ([cdrdv2-public.intel.com][3])                                                        |
| Entertainment Tonight – Breaking News | Celebrity Gossip | [http://feeds.feedburner.com/EtsBreakingNews](http://feeds.feedburner.com/EtsBreakingNews)                                                           | Very “headline-forward,” solid for quick daily hooks. ([About Facebook][1])                                                                            |
| Access Hollywood – Latest News        | Celebrity Gossip | [https://feeds.accesshollywood.com/AccessHollywood/LatestNews](https://feeds.accesshollywood.com/AccessHollywood/LatestNews)                         | Strong mainstream coverage + lots of bite-size stories. ([feeds.accesshollywood.com][4])                                                               |
| Deadline                              | Industry News    | [http://deadline.com/feed/](http://deadline.com/feed/)                                                                                               | Casting shakeups, deal/agency drama, awards/box office—great “inside baseball” without being academic. ([About Facebook][1])                           |
| The Hollywood Reporter – Live Feed    | Industry News    | [http://www.hollywoodreporter.com/blogs/live-feed/rss](http://www.hollywoodreporter.com/blogs/live-feed/rss)                                         | TV/film business + talent moves; may include TV items—filter out episode-recap keywords. ([About Facebook][1])                                         |
| Reuters – Entertainment               | Industry News    | [http://feeds.reuters.com/reuters/entertainment](http://feeds.reuters.com/reuters/entertainment)                                                     | Clean, factual entertainment business/news; less snark, good for “what happened” backbone.                                                             |
| CNN – Showbiz                         | Culture          | [http://rss.cnn.com/rss/cnn_showbiz.rss](http://rss.cnn.com/rss/cnn_showbiz.rss)                                                                     | Mainstream entertainment headlines; good for broad pop-culture moments. ([About Facebook][1])                                                          |
| Vulture (NYMag)                       | Culture          | [http://feeds.feedburner.com/nymag/vulture](http://feeds.feedburner.com/nymag/vulture)                                                               | Big culture convos + celeb/media angles; can overlap with TV—filter recaps and “episode” posts. ([About Facebook][1])                                  |
| The New Yorker – Culture              | Culture          | [http://www.newyorker.com/feed/culture](http://www.newyorker.com/feed/culture)                                                                       | More “essay-ish” but still culture-forward; use selectively for deeper context episodes. ([About Facebook][1])                                         |
| POPSUGAR                              | Culture          | [http://www.popsugar.com/feed](http://www.popsugar.com/feed)                                                                                         | Pop-culture + celeb moments + internet-y angles; high volume. ([About Facebook][1])                                                                    |
| People – Music                        | Music            | [https://feeds-api.dotdashmeredith.com/v1/rss/people/music](https://feeds-api.dotdashmeredith.com/v1/rss/people/music)                               | Music headlines with mainstream framing (artists, tours, drama).                                                                                       |
| Pitchfork – News                      | Music            | [https://pitchfork.com/feed/feed-news/rss](https://pitchfork.com/feed/feed-news/rss)                                                                 | Music industry + releases/controversies; great for “what fans are reacting to.”                                                                        |
| NME – News                            | Music            | [http://feeds2.feedburner.com/nmecom/rss/newsxml](http://feeds2.feedburner.com/nmecom/rss/newsxml)                                                   | High-frequency UK/US music news; good for quick hooks. ([About Facebook][1])                                                                           |
| Red Carpet Ready by Christina         | Red Carpet       | [https://redcarpetreadybychristina.ca/blogs/feed/](https://redcarpetreadybychristina.ca/blogs/feed/)                                                 | Styling/red-carpet focused; useful when awards/fashion moments spike.                                                                                  |
| The Fashion Tag                       | Red Carpet       | [https://thefashiontag.com/feed](https://thefashiontag.com/feed)                                                                                     | Red-carpet looks + fashion coverage (good “best/worst dressed” segments).                                                                              |

If you want, I can also output this as an **OPML** import file (so you can drop it into Feedly/Inoreader/your scraper pipeline), plus a **keyword filter pack** to prevent TV-recap overlap (e.g., block “recap”, “episode”, “season finale”, etc.) while still keeping major TV-business headlines (casting, renewals, cancellations).

[1]: https://about.fb.com/wp-content/uploads/2016/05/rss-urls-1.pdf?utm_source=chatgpt.com "RSS URLs"
[2]: https://celebitchy.com/site_announcements/?utm_source=chatgpt.com "Site Announcements Archives"
[3]: https://cdrdv2-public.intel.com/671419/610636-intel-media-accelerator-reference-software-linux-gold-user-guide-0.pdf?utm_source=chatgpt.com "Intel® Media Accelerator Reference Software for Linux*"
[4]: https://feeds.accesshollywood.com/AccessHollywood/LatestNews?utm_source=chatgpt.com "Entertainment News, Celebrity, TV, Music & Movie Videos"
