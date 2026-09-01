#!/usr/bin/env python
"""Re-runnable persona-load verifier for a Hermes profile.
Asserts on BEHAVIORAL markers, not literal foreign-language substrings,
because the persona may reply in the user's language (e.g. Spanish).

Usage:
    python verify_profile_soul.py <profile> <marker1> [marker2 ...]
Exits 0 if the profile's SOUL.md exists AND a real `hermes --profile`
chat reply contains >=2 of the markers (case-insensitive substring match).
"""
import os, sys, subprocess, re

def main():
    if len(sys.argv) < 3:
        print("usage: verify_profile_soul.py <profile> <marker1> [marker2 ...]")
        return 2
    profile, markers = sys.argv[1], sys.argv[2:]
    local = os.environ.get("LOCALAPPDATA", "")
    soul = os.path.join(local, "hermes", "profiles", profile, "SOUL.md")
    if not os.path.isfile(soul):
        print(f"FAIL: missing {soul}")
        return 1
    soul_low = open(soul, encoding="utf-8").read().lower()
    if sum(1 for m in markers if m.lower() in soul_low) < 2:
        print(f"FAIL: SOUL.md has <2 markers of {markers}")
        return 1
    # Real load test
    out = subprocess.run(
        ["hermes", "--profile", profile, "chat", "-q",
         "Identificate en una frase."],
        capture_output=True, text=True, timeout=120).stdout
    m = re.search(r"╮\s*(.*?)\s*╰", out, re.S)
    resp = (m.group(1) if m else out).strip()
    resp_low = resp.lower()
    hits = [mk for mk in markers if mk.lower() in resp_low]
    if len(hits) < 2:
        print(f"FAIL: persona did not load. reply='{resp[:200]}'")
        return 1
    print(f"PASS: profile={profile} soul={len(open(soul,encoding='utf-8').read())}b "
          f"markers={len(hits)}/{len(markers)} reply='{resp[:90]}'")
    return 0

if __name__ == "__main__":
    sys.exit(main())
