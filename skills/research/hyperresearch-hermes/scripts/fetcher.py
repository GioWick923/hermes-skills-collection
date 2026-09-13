#!/usr/bin/env python3
"""
fetcher.py — Parallel fetcher for research sources

Adapted from hyperresearch's fetcher concept.
Uses requests + markdownify for lightweight fetching.
For heavy JS sites, uses browser_exec via delegate_task.
"""
import requests
from markdownify import markdownify
from urllib.parse import urlparse
import hashlib
import time

def fetch_url(url, timeout=15):
    """Fetch a URL and convert to markdown"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        
        # Convert to markdown
        md = markdownify(r.text, heading_style="ATX")
        
        return {
            "success": True,
            "url": url,
            "title": extract_title(r.text),
            "content": md,
            "word_count": len(md.split()),
            "status_code": r.status_code
        }
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": str(e)
        }

def extract_title(html):
    """Extract title from HTML"""
    import re
    
    # Try <title> tag
    match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    if match:
        return match.group(1).strip()[:200]
    
    # Try OpenGraph
    match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html, re.IGNORECASE)
    if match:
        return match.group(1).strip()[:200]
    
    return "Untitled"

def get_domain(url):
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc

def infer_type(url, content):
    """Infer source type from URL and content"""
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    # Academic papers
    if any(x in path for x in ['.pdf', 'arxiv', 'doi', 'pmc']):
        return 'paper'
    
    # GitHub repos
    if 'github.com' in get_domain(url):
        return 'repository'
    
    # Long form content
    if len(content.split()) > 2000:
        return 'article'
    
    return 'webpage'

def fetch_batch(urls, max_concurrent=5):
    """Fetch multiple URLs with concurrency limit"""
    import asyncio
    from aiohttp import ClientSession, TCPConnector
    
    async def _fetch(session, url):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                text = await resp.text()
                md = markdownify(text, heading_style="ATX")
                return {
                    "success": True,
                    "url": url,
                    "title": extract_title(text),
                    "content": md,
                    "word_count": len(md.split()),
                    "type": infer_type(url, md)
                }
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}
    
    async def main():
        connector = TCPConnector(limit=max_concurrent)
        async with ClientSession(connector=connector) as session:
            tasks = [asyncio.create_task(_fetch(session, url)) for url in urls]
            return await asyncio.gather(*tasks)
    
    return asyncio.run(main())

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch URLs for research")
    parser.add_argument("--url", help="URL to fetch")
    parser.add_argument("--batch", nargs="+", help="Multiple URLs")
    
    args = parser.parse_args()
    
    if args.url:
        result = fetch_url(args.url)
        print(json.dumps(result, indent=2))
    
    elif args.batch:
        results = fetch_batch(args.batch)
        for r in results:
            status = "✅" if r["success"] else "❌"
            print(f"{status} {r['url']}: {r.get('title', 'Error')}")
