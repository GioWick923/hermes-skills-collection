#!/usr/bin/env python3
"""
Extract configuration from a running Forge Neo / Automatic1111 instance.
Usage: python extract-config.py [--url http://localhost:7860] [--params PARAM1 PARAM2]
"""

import argparse
import json
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def fetch_html(url: str) -> str:
    """Fetch the main page HTML."""
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8")
    except (URLError, HTTPError) as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        sys.exit(1)


def extract_gradio_config(html: str) -> dict:
    """Extract window.gradio_config from HTML."""
    match = re.search(r'window\.gradio_config\s*=\s*(\{.*?\});', html, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"Failed to parse gradio_config: {e}", file=sys.stderr)
        return {}


def get_state(config: dict) -> dict:
    """Extract state from config."""
    return config.get("state", {})


def format_output(state: dict, params: list[str] | None = None) -> str:
    """Format state dictionary for display."""
    if not params:
        # Show all params sorted
        lines = []
        for k in sorted(state.keys()):
            v = state[k]
            lines.append(f"{k}: {v}")
        return "\n".join(lines)
    
    # Show only requested params
    lines = []
    for p in params:
        # Try exact match first
        if p in state:
            lines.append(f"{p}: {state[p]}")
        else:
            # Try case-insensitive match
            matches = [k for k in state.keys() if k.lower() == p.lower()]
            if matches:
                lines.append(f"{matches[0]}: {state[matches[0]]}")
            else:
                lines.append(f"{p}: NOT_FOUND")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Extract Forge Neo / A1111 config")
    parser.add_argument("--url", default="http://localhost:7860", help="Base URL")
    parser.add_argument("--params", nargs="*", help="Specific params to show")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    # Fetch and parse
    html = fetch_html(args.url)
    config = extract_gradio_config(html)
    state = get_state(config)
    
    if not state:
        print("No state found in gradio_config", file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if args.json:
        if args.params:
            filtered = {p: state.get(p) for p in args.params}
            print(json.dumps(filtered, indent=2))
        else:
            print(json.dumps(state, indent=2))
    else:
        print(format_output(state, args.params))


if __name__ == "__main__":
    main()
