# Websearch Prompt - Today's Case Files

You are helping build a daily podcast network. The goal is to deliver high-quality, trustworthy news and stories so listeners do not need to scroll or read. Each show is a daily 12-15 minute podcast with 10 stories per episode. We prioritize sources that are reliable, frequently updated, and not hoax-prone.

Task
Find RSS/Atom feeds and other scrape-friendly sources for this show:
Today's Case Files (True Crime and Crime Stories)

Requirements
1. Focus on credible, consistent sources with frequent updates.
2. Prefer official or primary sources where possible.
3. Avoid sensational or rumor-heavy sites.
4. Provide 10-20 sources.
5. Include direct RSS or Atom feed URLs when available.
6. If no RSS feed, include a stable section URL that can be scraped.

Output Format (strict)
Return a single JSON object with this shape:

{
  "todays_case_files": [
    {
      "name": "Source Name",
      "type": "rss|atom|site|reddit|youtube",
      "url": "https://...",
      "notes": "Why it is valuable, update frequency, any caveats"
    }
  ]
}

Quality Filter
1. Prefer mainstream, fact-checked outlets, official agencies, and reputable niche sources.
2. If a source is less reliable but high-signal, mark it clearly in notes.
