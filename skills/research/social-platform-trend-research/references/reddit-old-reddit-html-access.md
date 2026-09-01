# Reddit access via old.reddit HTML (when JSON API is blocked)

## Problem observed
On the host used in the 2026-07-12 Hermes community scan, Reddit's JSON endpoints
returned empty/HTML bodies instead of JSON:
- `https://old.reddit.com/search.json?q=...` → empty body → `json.loads` raises `Expecting value: line 1 column 1 (char 0)`
- `https://old.reddit.com/r/<sub>/hot/.json` → HTML error page, not JSON
Status checks (`-w %{http_code}`) returned `200` for the HTML pages, confirming the
endpoint was alive but serving HTML, not the JSON API.

## Working recipe (old.reddit HTML)
1. List posts (hot/new/top):
   `curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" "https://old.reddit.com/r/hermesagent/hot/" -o list.html`
2. Extract post links + titles:
   `grep -oE '<p class="title"><a class="title may-blank[^"]*"[^>]+href="(/r/<sub>/comments/[^"]+)"[^>]*>([^<]+)</a>'`
   (html-unescape the title)
3. Fetch each post page and extract body + comments:
   regex over `<div class="usertext-body[^>]*>(.*?)</div>\s*</div>` (first match = post body,
   rest = comments). Clean with `re.sub('<[^>]+>',' ')` + `html.unescape` + whitespace collapse.
4. Subreddit pages that worked: `r/hermesagent` (unofficial community, actively posting).

## Notes
- Write scratch files under `$HOME` (e.g. `$HOME/hermes_scan/`), NOT `/tmp` — on MSYS/Windows
  hosts `/tmp` does NOT persist between separate `terminal` calls.
- X/Twitter unauthenticated search was not verifiably accessible — treat X findings as indirect
  unless you can read the original. Prefer Reddit/Google snippets as fallback and label them.
