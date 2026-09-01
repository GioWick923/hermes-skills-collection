#!/usr/bin/env python
"""Verify a Hermes profile: (1) SOUL.md exists + has the persona,
(2) a real chat resolves the API key and the persona actually loads.

Usage:  python scripts/verify_profile_live.py <profile> <marker1> [marker2 ...]
Exit 0 = pass, 1 = fail. Prints an ad-hoc verification line.

This replaces the brittle literal-substring asserts that false-negative on
non-English replies. Assert on behavioral markers instead.
"""
import os, sys, subprocess, re

LOCAL = os.environ.get("LOCALAPPDATA", "")
PROFILE = sys.argv[1]
MARKERS = [m.lower() for m in sys.argv[2:]]

soul = os.path.join(LOCAL, "hermes", "profiles", PROFILE, "SOUL.md")
assert os.path.isfile(soul), f"FALTA SOUL.md en perfil {PROFILE}"
txt = open(soul, encoding="utf-8").read()

# 1. SOUL content check
hits = [m for m in MARKERS if m in txt.lower()]
assert hits, f"persona incompleta en SOUL.md (ningun marcador de {MARKERS})"

# 2. Live chat: must resolve API key AND load persona
out = subprocess.run(
    ["hermes", "--profile", PROFILE, "chat", "-q", "Di tu rol en 6 palabras."],
    capture_output=True, text=True, timeout=120).stdout
m = re.search(r"╮\s*(.*?)\s*╰", out, re.S)
resp = (m.group(1) if m else out).strip()

# API-key failure signature
if "empty API key" in out or "Goodbye!" in out and "empty" in out:
    raise SystemExit(f"FAIL: {PROFILE} NO resuelve la API key (.env ausente?) -> {resp[:160]}")

assert any(k in resp.lower() for k in MARKERS), f"perfil no cargo la persona: {resp[:200]}"
print(f"VERIF AD-HOC {PROFILE}: soul={len(txt)}b | apikey=OK | persona=SI | resp='{resp[:90]}'")
