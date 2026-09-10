#!/usr/bin/env python3
"""
search-cases.py — Busca prompts industriales de gpt-image-2

Usage:
    python search-cases.py --category "Products & E-commerce" --style Product
    python search-cases.py --keyword "volumetric lighting"
    python search-cases.py --scene Fashion --count 3
    python search-cases.py --random 5
"""
import argparse, json, os, random, sys

CASES_FILE = os.path.join(os.path.dirname(__file__), "..", "references", "gpt-image-2-cases.json")

def load_cases():
    with open(CASES_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("cases", [])

def main():
    parser = argparse.ArgumentParser(description="Search gpt-image-2 industrial prompts")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--style", help="Filter by style")
    parser.add_argument("--scene", help="Filter by scene")
    parser.add_argument("--keyword", help="Search in prompt text")
    parser.add_argument("--count", type=int, default=5, help="Number of results")
    parser.add_argument("--random", type=int, metavar="N", help="Get N random cases")
    parser.add_argument("--list-categories", action="store_true", help="List all categories")
    parser.add_argument("--list-styles", action="store_true", help="List all styles")
    parser.add_argument("--list-scenes", action="store_true", help="List all scenes")
    args = parser.parse_args()

    cases = load_cases()

    if args.list_categories:
        cats = sorted(set(c.get("category", "") for c in cases))
        for cat in cats:
            count = sum(1 for c in cases if c.get("category") == cat)
            print(f"  {cat:30s} ({count})")
        return

    if args.list_styles:
        styles = sorted(set(s for c in cases for s in c.get("styles", [])))
        for s in styles:
            count = sum(1 for c in cases if s in c.get("styles", []))
            print(f"  {s:20s} ({count})")
        return

    if args.list_scenes:
        scenes = sorted(set(s for c in cases for s in c.get("scenes", [])))
        for sc in scenes:
            count = sum(1 for c in cases if sc in c.get("scenes", []))
            print(f"  {sc:15s} ({count})")
        return

    if args.random:
        results = random.sample(cases, min(args.random, len(cases)))
    else:
        # Filter
        results = cases
        if args.category:
            results = [c for c in results if c.get("category", "").lower() == args.category.lower()]
        if args.style:
            results = [c for c in results if args.style.lower() in [s.lower() for s in c.get("styles", [])]]
        if args.scene:
            results = [c for c in results if args.scene.lower() in [s.lower() for s in c.get("scenes", [])]]
        if args.keyword:
            kw = args.keyword.lower()
            results = [c for c in results if kw in c.get("prompt", "").lower() or kw in c.get("promptPreview", "").lower()]

        # Limit
        results = results[:args.count]

    if not results:
        print("No results found.")
        return

    print(f"=== {len(results)} results ===\n")
    for i, c in enumerate(results, 1):
        title = c.get('title', f"Case {c.get('id')}")
        print(f"--- {i}. {title} ---")
        print(f"   ID: {c.get('id')}")
        print(f"   Category: {c.get('category')}")
        print(f"   Styles: {', '.join(c.get('styles', []))}")
        print(f"   Scenes: {', '.join(c.get('scenes', []))}")
        prompt = c.get('prompt', '')
        preview = prompt[:300].replace('\n', ' ')
        if len(prompt) > 300:
            preview += "..."
        print(f"   Prompt: {preview}")
        print(f"   Source: {c.get('sourceLabel', '')} - {c.get('sourceUrl', '')}")
        print()

if __name__ == "__main__":
    main()