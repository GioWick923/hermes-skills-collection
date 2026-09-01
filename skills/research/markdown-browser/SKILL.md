---
name: markdown-browser
description: Lightweight HTML-to-Markdown browser with viewport paging.
---

# Markdown Browser

A lightweight, read-only web browser that fetches HTML via `requests`, converts to Markdown, and operates on the text. No JavaScript, no browser binary. Ported concept from HKUDS/Auto-Deep-Research `autoagent/environment/markdown_browser/`.

Use when:
- The heavy browser stack is unavailable, slow, or overkill
- You need to extract clean text/content from a page for analysis
- You want deterministic, cheap page reads (vs. rendering a full browser)

## Core interface (abstract)

```
set_address(uri)          # navigate to URL
viewport                  # current visible slice of page content
page_content              # full markdown of current page
page_down() / page_up()   # move viewport by ~viewport_size chars
visit_page(path_or_uri)   # fetch + convert + return viewport
open_local_file(path)     # read local file as markdown
find_on_page(query)       # regex/substring search, return match context
search(query)             # Bing/DDG fallback search -> markdown results
```

## Implementation sketch (Python)

```python
import requests, re, html
from urllib.parse import urljoin, urlparse
from markdownify import markdownify  # or use mdconvert.py from source

class MarkdownBrowser:
    def __init__(self, viewport_size=8192, start_page="about:blank"):
        self.viewport_size = viewport_size
        self.history = []
        self.page_content = ""
        self.viewport_current_page = 0
        self.set_address(start_page)

    def set_address(self, uri):
        self.address = uri
        if uri and uri != "about:blank":
            self.visit_page(uri)

    def visit_page(self, uri):
        resp = requests.get(uri, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        raw_html = resp.text
        md = markdownify(raw_html, heading_style="ATX")
        self.page_content = md
        self.viewport_current_page = 0
        self.history.append((uri, time.time()))
        return self.viewport

    @property
    def viewport(self):
        chars = self.page_content
        start = self.viewport_current_page * self.viewport_size
        return chars[start:start + self.viewport_size]

    def page_down(self):
        self.viewport_current_page += 1
        return self.viewport

    def page_up(self):
        self.viewport_current_page = max(0, self.viewport_current_page - 1)
        return self.viewport

    def find_on_page(self, query):
        idx = self.page_content.find(query)
        if idx == -1:
            return None
        return self.page_content[max(0, idx-200):idx+200]
```

## Search fallback

If no API key, submit a GET to Bing/DDG HTML and scrape results:
```python
def search(self, query):
    resp = requests.get("https://html.duckduckgo.com/html/", params={"q": query},
                        headers={"User-Agent": "Mozilla/5.0"})
    # parse result links + snippets from HTML, return as markdown
```
Prefer the dedicated `web_search` tool or `web_extract` when available — this is the fallback for constrained environments.

## Advantages over full browser

- **Zero dependencies** beyond `requests` + a markdown converter
- **Fast, cheap, deterministic** — no rendering, no flakiness
- **Token-efficient** — viewport paging limits context window usage
- **Safe** — no JS execution, no browser exploits

## Limitations

- Cannot interact with JS-heavy apps (SPA, login walls, dynamic content)
- No screenshots, no clicks
- For those, use the heavy browser stack

## Source

Ported from https://github.com/HKUDS/Auto-Deep-Research (MIT-compatible, AutoAgent framework). Reference files:
- `autoagent/environment/markdown_browser/abstract_markdown_browser.py`
- `autoagent/environment/markdown_browser/requests_markdown_browser.py`
- `autoagent/environment/markdown_browser/markdown_search.py`
