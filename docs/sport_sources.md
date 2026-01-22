This selection focuses on active, high-yield feeds that prioritize narrative, rumors, and "hooky" headlines over dry statistics. These are chosen specifically to feed a short-form video automation system (TikTok/Reels/Shorts) where emotional engagement and debate are critical.

Top Recommended Sports RSS Feeds
Source Name	Category	Feed URL (Copy & Paste)	Content Notes (Tone & "Hook" Potential)
Yardbarker	Multi-Sport / Rumors	https://www.yardbarker.com/rss/headlines	High Priority. Aggregates the best rumors and "gossip" from across the web. Excellent for finding "He said/She said" drama and trade speculation.
ClutchPoints	NBA / Viral / Gen Z	https://clutchpoints.com/feed	Visual/Viral focus. Headlines are written specifically for the social media generation. Heavy focus on player drama, quotes, and "savage" moments.
HoopsHype	NBA	https://hoopshype.com/feed	The Gold Standard for NBA Drama. Covers trade rumors, agent leaks, and player social media beefs. Essential for NBA storylines.
ProFootballTalk	NFL	https://profootballtalk.nbcsports.com/feed	Opinionated/Snarky. Mike Florio’s site drives the NFL news cycle. Headlines are often provocative and perfect for sparking debate in comments.
CBS Sports	NFL (Mainstream)	https://www.cbssports.com/rss/headlines/nfl	Reliable/Fast. Good mix of breaking news (injuries, scores) and analysis. Use this for factual verification and "breaking" updates.
Yahoo Sports	Multi-Sport	https://sports.yahoo.com/rss	Human Interest. Yahoo often finds the "human" angle or the weird side story in games, which works well for 60-second storytelling.
MLB Trade Rumors	MLB	https://www.mlbtraderumors.com/feed	Transaction Heavy. During the season and winter meetings, this is the #1 source for trade hooks. US fans love trade speculation.
Awful Announcing	Sports Media / Culture	https://awfulannouncing.com/feed	Meta-Commentary. Covers what announcers said, broadcast fails, and media controversies. Great for "Did you hear what [Name] said?" hooks.
The Big Lead	Sports Culture	https://thebiglead.com/feed	Opinion/Hot Takes. Focuses on the intersection of sports and pop culture. Good for segments that aren't just about box scores.
Daily Snark	NFL / Humor	https://dailysnark.com/feed	Meme/Humor. Focuses heavily on the internet's reaction to sports events (memes, funny tweets). Great for lighthearted TikTok content.
Implementation Strategy for Automation

The "Rumor Mill" Filter: Set your scraper to prioritize keywords like "Rumor," "Trade," "Leak," "Unhappy," and "Demand" from Yardbarker and HoopsHype. These create the strongest hooks (e.g., "You won't believe who wants out of LA...").

The "Debate" Filter: Use ProFootballTalk and The Big Lead to find opinionated takes. Automate a script that summarizes the "Hot Take" and asks the user, "Is he right?" to drive engagement.

The "Results" Layer: Use CBS Sports or Yahoo purely for factual results (Scores, Injuries) to overlay text on your video visuals.

Technical Note:
Most of these feeds provide a description or content:encoded tag. For automated scripts, parse the description for the summary hook, but always link back to the source for the full narrative context required for your 7-10 minute podcast segment.

| Source Name | Category | Feed URL | Notes |
|-------------|----------|----------|-------|
| ESPN NFL Headlines | NFL | https://www.espn.com/espn/rss/nfl/news | Engaging tone with highlights, storylines, and analysis; updates multiple times daily; no known issues, free access. |
| ESPN NBA Headlines | NBA | https://www.espn.com/espn/rss/nba/news | Fan-focused narratives on games, trades, and injuries; frequent updates during season; accessible without login. |
| ESPN MLB Headlines | MLB | https://www.espn.com/espn/rss/mlb/news | Covers results, key moments, and controversies; in-season focus with daily posts; light, entertaining style. |
| ESPN NHL Headlines | NHL | https://www.espn.com/espn/rss/nhl/news | Includes playoff races and viral moments; updates regularly; suitable for short hooks and deeper stories. |
| ESPN Top Headlines | Multi-Sport | https://www.espn.com/espn/rss/news | Mix of breaking news across sports; high frequency; energetic tone, ideal for broad coverage. |
| Bleacher Report NFL | NFL | https://bleacherreport.com/articles/feed?tag_id=18 | Edgy, opinionated takes on news and rumors; daily updates; fan-oriented, no paywall. |
| Bleacher Report NBA | NBA | https://bleacherreport.com/articles/feed?tag_id=19 | Viral moments and storylines; frequent posts; engaging for TikTok-style content. |
| Bleacher Report MLB | MLB | https://bleacherreport.com/articles/feed?tag_id=23 | Trades, injuries, and highlights; in-season daily; fun, narrative-driven. |
| Yahoo Sports NFL News | NFL | https://sports.yahoo.com/nfl/news/rss/ | Results, controversies, and analysis; multiple daily updates; casual tone, free. |
| Yahoo Sports NBA News | NBA | https://sports.yahoo.com/nba/news/rss/ | Key moments and trades; regular updates; suitable for hooks and podcast segments. |
| Yahoo Sports MLB News | MLB | https://sports.yahoo.com/mlb/news/rss/ | Game recaps and storylines; seasonal frequency; engaging, no issues. |
| Yahoo Sports NHL News | NHL | https://sports.yahoo.com/nhl/news/rss/ | Injuries and playoff news; daily during season; light-hearted coverage. |
| CBS Sports NFL Headlines | NFL | https://www.cbssports.com/rss/headlines/nfl | Breaking news and expert picks; frequent; analytical yet accessible tone. |
| CBS Sports NBA Headlines | NBA | https://www.cbssports.com/rss/headlines/nba | Stats, stories, and controversies; multiple updates; fan-friendly. |
| Fox Sports Breaking News | Breaking News | https://api.foxsports.com/v2/content/optimized-rss?partnerKey=MB0Wehpmuj2lUhuRhQaafhBjAJqaPU244mlTDK1i&size=30 | Real-time updates on major events; high frequency; exciting, sports-centric tone. |
| SB Nation Main Feed | Multi-Sport | https://www.sbnation.com/rss/current | Fan-driven stories and breaking news; daily; community-oriented, no paywall. |


Here are high-quality, **active RSS feeds** that work well for automated scraping across **NFL + NBA core**, plus **MLB + NHL in-season**, with a mix of **results, breaking news, storylines, trades, injuries, and viral moments**.

| Source Name                          | Category      | Feed URL                                                                                          | Notes (tone, frequency, any issues)                                                                      |
| ------------------------------------ | ------------- | ------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| ESPN – Top Headlines                 | Multi-Sport   | `https://www.espn.com/espn/rss/news`                                                              | Fast, mainstream, lots of “hookable” headlines; snippets can be short. ([ESPN.com][1])                   |
| CBS Sports – Headlines               | Multi-Sport   | `https://www.cbssports.com/rss/headlines/`                                                        | Very active; good mix of results + storylines; generally punchy. ([CBS Sports][2])                       |
| FOX Sports – Top News                | Breaking News | `https://api.foxsports.com/v1/rss?partnerKey=MB0Wehpm5Ac7T4fn8T2x3w&tag=sport&category=foxsports` | Great for quick hooks; frequent updates. ([Fox Sports][3])                                               |
| USA TODAY – Sports                   | Multi-Sport   | `http://content.usatoday.com/marketing/rss/rsstrans.aspx?feedId=sports1`                          | Broad US sports coverage; good for “what you missed today” rundowns. ([About Facebook][4])               |
| Sports Illustrated – Top Stories     | Multi-Sport   | `http://www.si.com/rss/si_topstories.rss`                                                         | More narrative/feature flavor than pure scores; still timely. ([About Facebook][4])                      |
| Yahoo Sports – Top                   | Multi-Sport   | `https://sports.yahoo.com/top/rss.xml`                                                            | High volume; often strong context for podcast expansion. ([About Facebook][4])                           |
| Deadspin – Full Feed                 | Multi-Sport   | `http://feeds.gawker.com/deadspin/full`                                                           | More edge/controversy/viral moments; useful for short-form hooks. ([About Facebook][4])                  |
| ESPN – NFL                           | NFL           | `https://www.espn.com/espn/rss/nfl/news`                                                          | Breaking news + injuries + league storylines; headline-dense. ([ESPN.com][1])                            |
| CBS Sports – NFL                     | NFL           | `https://www.cbssports.com/rss/headlines/nfl/`                                                    | Very active; strong for weekly arcs + playoff race framing. ([CBS Sports][2])                            |
| FOX Sports – NFL                     | NFL           | `https://api.foxsports.com/v1/rss?partnerKey=MB0Wehpm5Ac7T4fn8T2x3w&tag=nfl&category=article`     | Quick hit headlines; good “clipable” phrasing. ([Fox Sports][3])                                         |
| RealGM – NFL Wiretap                 | NFL           | `https://football.realgm.com/rss/realgm_nfl_wiretap.xml`                                          | Aggregated storyline feed (rumors/injuries/trades); solid context in entries. ([football.realgm.com][5]) |
| ESPN – NBA                           | NBA           | `https://www.espn.com/espn/rss/nba/news`                                                          | Great for breaking news + stars; reliable daily volume. ([ESPN.com][1])                                  |
| CBS Sports – NBA                     | NBA           | `https://www.cbssports.com/rss/headlines/nba/`                                                    | Strong for game-night arcs + controversy; frequent updates. ([CBS Sports][2])                            |
| FOX Sports – NBA                     | NBA           | `https://api.foxsports.com/v1/rss?partnerKey=MB0Wehpm5Ac7T4fn8T2x3w&tag=nba&category=article`     | Fast, headline-forward; good for TikTok hooks. ([Fox Sports][3])                                         |
| RealGM – NBA Wiretap                 | NBA           | `http://basketball.realgm.com/rss/realgm_nba_wiretap.xml`                                         | Excellent for trade/injury/rumor aggregation; high utility for automation. ([forums.realgm.com][6])      |
| ESPN – MLB                           | MLB           | `https://www.espn.com/espn/rss/mlb/news`                                                          | In-season news + transactions; steady volume. ([ESPN.com][1])                                            |
| CBS Sports – MLB                     | MLB           | `https://www.cbssports.com/rss/headlines/mlb/`                                                    | Good mix of results + storylines + roster moves. ([CBS Sports][2])                                       |
| FOX Sports – MLB                     | MLB           | `https://api.foxsports.com/v1/rss?partnerKey=MB0Wehpm5Ac7T4fn8T2x3w&tag=mlb&category=article`     | Quick headlines; helpful for daily “3 things” format. ([Fox Sports][3])                                  |
| RealGM – MLB Wiretap                 | MLB           | `https://baseball.realgm.com/rss/realgm_mlb_wiretap.xml`                                          | Aggregated rumors/trades/news; good context chunks. ([RealGM Baseball][7])                               |
| MLB Trade Rumors – Main              | MLB           | `http://feeds.feedburner.com/MlbTradeRumors`                                                      | Elite for trades/rumors; very “podcastable” narrative. ([mlbtraderumors.com][8])                         |
| MLB Trade Rumors – Transactions Only | MLB           | `http://feeds.feedburner.com/MLBTRTransactions`                                                   | Clean “just what happened” feed—great for automated recaps. ([mlbtraderumors.com][9])                    |
| ESPN – NHL                           | NHL           | `https://www.espn.com/espn/rss/nhl/news`                                                          | Injuries, trades, playoff race framing; steady feed. ([ESPN.com][1])                                     |
| CBS Sports – NHL                     | NHL           | `https://www.cbssports.com/rss/headlines/nhl/`                                                    | Frequent updates; good “what matters tonight” headlines. ([CBS Sports][2])                               |
| FOX Sports – NHL                     | NHL           | `https://api.foxsports.com/v1/rss?partnerKey=MB0Wehpm5Ac7T4fn8T2x3w&tag=nhl&category=article`     | Fast, hooky headlines; good for short clips. ([Fox Sports][3])                                           |
| RealGM – NHL Wiretap                 | NHL           | `https://hockey.realgm.com/rss/realgm_nhl_wiretap.xml`                                            | Aggregated news + rumors with decent context; automation-friendly. ([hockey.realgm.com][10])             |
| The Hockey Writers – Global          | NHL           | `https://thehockeywriters.com/feed/`                                                              | Great analysis + storylines; less “scoreboard,” more narrative. ([The Hockey Writers][11])               |

If you want, I can also suggest a **dedupe + prioritization** approach (e.g., “Breaking first, then Wiretap aggregation, then feature/analysis”) so your system avoids posting the same story 6 times from ESPN/CBS/FOX.

[1]: https://www.espn.com/espn/news/story?id=3437834 "RSS Index - ESPN"
[2]: https://www.cbssports.com/xml/rss "RSS News Feeds - CBSSports.com "
[3]: https://www.foxsports.com/rss-feeds "FOX SPORTS RSS FEEDS | FOX Sports"
[4]: https://about.fb.com/wp-content/uploads/2016/05/rss-urls-1.pdf?utm_source=chatgpt.com "RSS URLs"
[5]: https://football.realgm.com/news/ "NFL News, Football Rumors - RealGM"
[6]: https://forums.realgm.com/boards/viewtopic.php?f=40&t=1012121&utm_source=chatgpt.com "RSS Feed Bug"
[7]: https://baseball.realgm.com/news/ "MLB News, Baseball Rumors - RealGM"
[8]: https://www.mlbtraderumors.com/2007/10/subscribe-to-ou.html?utm_source=chatgpt.com "Subscribe To Our RSS Feed"
[9]: https://www.mlbtraderumors.com/2009/07/mlbtr-transactionsonly-rss-feed.html?utm_source=chatgpt.com "MLBTR Transactions-Only RSS Feed"
[10]: https://hockey.realgm.com/news/ "NHL News, Hockey Rumors - RealGM"
[11]: https://thehockeywriters.com/the-hockey-writers-rss-feeds/?utm_source=chatgpt.com "The Hockey Writers RSS Feeds"
  

Source Name,Category,Feed URL,Tier,Notes
ESPN - NFL,NFL,https://www.espn.com/espn/rss/nfl/news,1,"High frequency, breaking news, ~50+ items/day during season"
ESPN - NBA,NBA,https://www.espn.com/espn/rss/nba/news,1,"Comprehensive coverage, trades, injuries, analysis"
ESPN - MLB,MLB,https://www.espn.com/espn/rss/mlb/news,1,In-season use (April-October)
ESPN - NHL,NHL,https://www.espn.com/espn/rss/nhl/news,1,In-season use (October-June)
ESPN - Top Headlines,Multi-Sport,https://www.espn.com/espn/rss/news,1,"Cross-sport breaking news, viral moments"
CBS Sports - NFL,NFL,https://www.cbssports.com/rss/headlines/nfl,1,"Solid analysis, fantasy angles"
CBS Sports - NBA,NBA,https://www.cbssports.com/rss/headlines/nba,1,Good for storylines and expert picks
CBS Sports - MLB,MLB,https://www.cbssports.com/rss/headlines/mlb,1,Strong fantasy/stats content
CBS Sports - NHL,NHL,https://www.cbssports.com/rss/headlines/nhl,1,Reliable in-season coverage
CBS Sports - General,Multi-Sport,https://www.cbssports.com/rss/headlines/,1,All sports headlines combined
Yahoo Sports - NFL,NFL,https://sports.yahoo.com/nfl/rss,2,"Strong breaking news, no paywall"
Yahoo Sports - NBA,NBA,https://sports.yahoo.com/nba/rss,2,"Insider scoops, trade rumors"
Yahoo Sports - MLB,MLB,https://sports.yahoo.com/mlb/rss,2,Solid in-season coverage
Yahoo Sports - NHL,NHL,https://sports.yahoo.com/nhl/rss,2,Reliable hockey news
Yahoo Sports - General,Multi-Sport,https://sports.yahoo.com/rss,2,All sports combined feed
NBC Sports - NFL,NFL,https://www.nbcsports.com/nfl.atom,2,Atom format. Pro Football Talk included
NBC Sports - NBA,NBA,https://www.nbcsports.com/nba.atom,2,Good analysis pieces
NBC Sports - MLB,MLB,https://www.nbcsports.com/mlb.atom,2,In-season use
NBC Sports - NHL,NHL,https://www.nbcsports.com/nhl.atom,2,Strong hockey coverage (NHL rights)
SB Nation - Main,Multi-Sport,https://www.sbnation.com/rss/current.xml,3,"Fan perspective, hot takes, narrative-driven"
SB Nation - NFL,NFL,https://www.sbnation.com/nfl/rss/current,3,"Team-specific angles, fan reactions"
SB Nation - NBA,NBA,https://www.sbnation.com/nba/rss/current,3,"Trade drama, player storylines"
SB Nation - MLB,MLB,https://www.sbnation.com/mlb/rss/current,3,In-season use
SB Nation - NHL,NHL,https://www.sbnation.com/nhl/rss/current,3,In-season use
RotoWire - NFL,NFL,https://www.rotowire.com/rss/nfl.xml,4,"Real-time player news, injuries, transactions"
RotoWire - NBA,NBA,https://www.rotowire.com/rss/nba.xml,4,"Instant player updates, lineup changes"
RotoWire - MLB,MLB,https://www.rotowire.com/rss/mlb.xml,4,"Pitching changes, lineup news"
RotoWire - NHL,NHL,https://www.rotowire.com/rss/nhl.xml,4,"Goalie starts, injury updates"
Fox Sports,Multi-Sport,https://api.foxsports.com/v2/content/optimized-rss?partnerKey=MB0Wehpmvph0EC04,5,General feed - verify API key
Sporting News,Multi-Sport,https://www.sportingnews.com/us/rss,5,"Analysis, rankings, features"
ClutchPoints,Multi-Sport,https://clutchpoints.com/feed,5,"Viral-friendly, social-first style"