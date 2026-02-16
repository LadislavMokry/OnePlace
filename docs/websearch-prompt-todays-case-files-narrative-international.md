# Websearch Prompt - Today's Case Files (Narrative + International)

You are helping build a daily true-crime podcast called "Today's Case Files." We need sources that are narrative, engaging, and international, not just official press releases.

Task
Find 10-20 sources from outside the U.S. and from long-form investigative outlets anywhere. Prioritize sources that are credible, updated regularly, and story-driven (not tabloids).

Requirements
1. Prefer RSS or Atom feeds when possible.
2. If no RSS, include a stable section URL that can be scraped.
3. Mark any source that is high-signal but potentially lower reliability.
4. Include a short note explaining why each source is useful for storytelling.

Output Format (strict JSON)

{
  "todays_case_files_narrative_international": [
    {
      "name": "Source Name",
      "type": "rss|atom|site|reddit|youtube",
      "url": "https://...",
      "notes": "Why it is valuable, update cadence, any caveats"
    }
  ]
}
