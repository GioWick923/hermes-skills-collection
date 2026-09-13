#!/usr/bin/env python3
"""
prompts-chat.py — Interface con la API de prompts.chat

The world's largest open-source prompt library (170k stars, 15k+ prompts).
API: https://prompts.chat/api/prompts

Usage:
    python prompts-chat.py --search "coding agent" --limit 5
    python prompts-chat.py --slug "pharmacy-chronic-patient-crm"
    python prompts-chat.py --random 3
    python prompts-chat.py --list-searches "development"
"""
import argparse
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

API_BASE = "https://prompts.chat/api"

def fetch_prompts(search=None, limit=5, offset=0):
    """Fetch prompts from prompts.chat API"""
    params = f"?limit={limit}&offset={offset}"
    if search:
        params += f"&search={urllib.parse.quote(search)}"
    
    url = f"{API_BASE}/prompts{params}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Hermes-Agent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Error HTTP {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def get_prompt_by_slug(slug):
    """Get a specific prompt by slug"""
    url = f"{API_BASE}/prompts/{slug}"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Hermes-Agent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Error HTTP {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(
        description="Search and retrieve prompts from prompts.chat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python prompts-chat.py --search "coding agent" --limit 3
  python prompts-chat.py --slug "pharmacy-chronic-patient-crm"
  python prompts-chat.py --random 5
  python prompts-chat.py --search "llm" --format json
        """
    )
    
    parser.add_argument("--search", help="Search query")
    parser.add_argument("--slug", help="Get prompt by slug")
    parser.add_argument("--random", type=int, metavar="N", help="Get N random prompts")
    parser.add_argument("--limit", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--offset", type=int, default=0, help="Pagination offset")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--stats", action="store_true", help="Show prompt library stats")
    
    args = parser.parse_args()
    
    # Stats mode
    if args.stats:
        data = fetch_prompts(limit=1)
        if data:
            total = data.get("total", 0)
            pages = data.get("totalPages", 0)
            print(f"📚 Prompts.chat Library")
            print(f"   Total prompts: {total:,}")
            print(f"   Pages: {pages}")
            print(f"   API: https://prompts.chat/api/prompts")
            print(f"   Website: https://prompts.chat")
            print(f"\n💡 Search example:")
            print(f"   python prompts-chat.py --search \"coding\" --limit 3")
        return
    
    # Single prompt by slug
    if args.slug:
        prompt = get_prompt_by_slug(args.slug)
        if prompt and args.format == "json":
            print(json.dumps(prompt, indent=2))
        elif prompt:
            print(f"# {prompt.get('title', 'N/A')}")
            print(f"Slug: {args.slug}")
            print(f"\n{prompt.get('content', '')}")
        return
    
    # Random prompts
    if args.random:
        # Fetch enough to pick from
        data = fetch_prompts(limit=args.random * 3, offset=0)
        if data and data.get("prompts"):
            import random as rnd
            selected = rnd.sample(data["prompts"], min(args.random, len(data["prompts"])))
            if args.format == "json":
                print(json.dumps(selected, indent=2))
            else:
                for i, p in enumerate(selected, 1):
                    print(f"\n{'='*60}")
                    print(f"#{i} {p.get('title', 'N/A')}")
                    print(f"Slug: {p.get('slug', 'N/A')}")
                    content = p.get('content', '')[:500]
                    print(f"\n{content}{'...' if len(p.get('content', '')) > 500 else ''}")
        return
    
    # Search prompts
    if args.search:
        data = fetch_prompts(search=args.search, limit=args.limit, offset=args.offset)
        if data and args.format == "json":
            print(json.dumps(data, indent=2))
        elif data:
            total = data.get("total", 0)
            print(f"🔍 Found {total} prompts for '{args.search}'\n")
            
            for i, p in enumerate(data.get("prompts", []), 1):
                print(f"{'='*60}")
                print(f"#{i} {p.get('title', 'N/A')}")
                print(f"Slug: {p.get('slug', 'N/A')}")
                if p.get('description'):
                    print(f"Desc: {p['description']}")
                content = p.get('content', '')[:300]
                print(f"\n{content}{'...' if len(p.get('content', '')) > 300 else ''}")
        return
    
    # Default: show help
    parser.print_help()

if __name__ == "__main__":
    main()
