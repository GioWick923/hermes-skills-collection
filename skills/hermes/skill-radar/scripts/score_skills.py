#!/usr/bin/env python3
"""Calculate evidence-adjusted value and risk scores for Skill Radar candidates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


OPPORTUNITY = {
    "fit": 0.20,
    "demand": 0.10,
    "leverage": 0.15,
    "quality": 0.10,
    "github_heat": 0.15,
    "x_heat": 0.10,
    "momentum": 0.05,
    "maintenance": 0.10,
    "uniqueness": 0.05,
}
RISK = {
    "permissions": 0.25,
    "execution": 0.20,
    "network": 0.15,
    "secrets": 0.15,
    "obfuscation": 0.10,
    "provenance": 0.10,
    "mismatch": 0.05,
}


def clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def weighted(scores: dict, weights: dict[str, float]) -> tuple[float, list[str]]:
    present = {}
    missing = []
    for key, weight in weights.items():
        value = scores.get(key)
        if value is None:
            missing.append(key)
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} must be a number from 0 to 100 or null")
        if not 0 <= value <= 100:
            raise ValueError(f"{key} must be from 0 to 100")
        present[key] = (float(value), weight)
    if not present:
        return 0.0, missing
    weight_sum = sum(weight for _, weight in present.values())
    result = sum(value * weight for value, weight in present.values()) / weight_sum
    return result, missing


def default_action(value: float, risk: float, confidence: float, hard_gate: bool) -> str:
    if hard_gate:
        return "quarantine"
    if value >= 75 and risk < 30 and confidence >= 70:
        return "adopt-or-sandbox-test"
    if value >= 60:
        return "shortlist-and-test"
    if value >= 40:
        return "watch"
    return "ignore"


def score(candidate: dict) -> dict:
    scores = candidate.get("scores", {})
    opportunity, missing_opportunity = weighted(scores, OPPORTUNITY)
    risk, missing_risk = weighted(scores, RISK)
    confidence = scores.get("evidence_confidence", 0)
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError("evidence_confidence must be a number from 0 to 100")
    confidence = clamp(float(confidence))
    factor = 0.4 + 0.6 * confidence / 100
    value = clamp(opportunity * factor - 0.35 * risk)
    hard_gate = bool(candidate.get("hard_gate", False))
    result = dict(candidate)
    result["radar"] = {
        "opportunity": round(opportunity, 1),
        "confidence": round(confidence, 1),
        "risk": round(risk, 1),
        "value_score": round(value, 1),
        "action": default_action(value, risk, confidence, hard_gate),
        "missing_scores": missing_opportunity + missing_risk,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="JSON array or object with a candidates array")
    parser.add_argument("-o", "--output", type=Path, help="Write scored JSON to this file")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    candidates = data.get("candidates", []) if isinstance(data, dict) else data
    if not isinstance(candidates, list):
        raise ValueError("input must be an array or an object containing a candidates array")

    scored = [score(candidate) for candidate in candidates]
    scored.sort(key=lambda item: item["radar"]["value_score"], reverse=True)
    payload = {"candidates": scored} if isinstance(data, dict) else scored
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
