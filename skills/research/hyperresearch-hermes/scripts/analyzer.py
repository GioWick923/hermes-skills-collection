#!/usr/bin/env python3
"""
analyzer.py — Analysis tools for research corpus

Extracts claims, quotes, contradictions from collected sources.
"""
import json
from pathlib import Path
from datetime import datetime

def analyze_corpus(run_dir, sources):
    """Analyze a corpus of sources"""
    analysis = {
        "run_id": run_dir.name,
        "analyzed_at": datetime.now().isoformat(),
        "source_count": len(sources),
        "total_words": sum(s.get("word_count", 0) for s in sources),
        "topics": extract_topics(sources),
        "claims": extract_claims(sources),
        "contradictions": find_contrastions(sources)
    }
    
    # Save analysis
    analysis_file = run_dir / "analysis.json"
    analysis_file.write_text(json.dumps(analysis, indent=2, default=str))
    
    return analysis

def extract_topics(sources):
    """Extract common topics from sources"""
    from collections import Counter
    
    all_topics = []
    for src in sources:
        all_topics.extend(src.get("topics", []))
    
    return Counter(all_topics).most_common(10)

def extract_claims(sources, max_claims=20):
    """Extract key claims from sources (simplified)"""
    claims = []
    
    for src in sources:
        content = src.get("content", "")
        # Simple claim extraction: look for declarative sentences
        sentences = content.split('. ')
        
        for sent in sentences[:5]:  # First 5 sentences per source
            if len(sent.strip()) > 50:  # Reasonable length
                claims.append({
                    "source_id": src.get("id"),
                    "claim": sent.strip()[:200],
                    "confidence": "medium"
                })
    
    return claims[:max_claims]

def find_contrastions(sources):
    """Find potential contradictions between sources"""
    contradictions = []
    
    # This is a simplified version
    # Full implementation would use LLM to detect contradictions
    for i, src1 in enumerate(sources):
        for src2 in sources[i+1:]:
            # Check for opposite claims
            pass  # TODO: Implement proper contradiction detection
    
    return contradictions

def generate_digest(run_dir, sources, max_claims=10):
    """Generate evidence digest"""
    digest = {
        "generated_at": datetime.now().isoformat(),
        "source_count": len(sources),
        "top_claims": [],
        "key_quotes": []
    }
    
    # Extract top claims
    claims = extract_claims(sources, max_claims)
    digest["top_claims"] = claims
    
    # Extract key quotes (simplified)
    for src in sources[:5]:
        content = src.get("content", "")
        # Find interesting quotes
        quotes = [s.strip() for s in content.split('.') if '"' in s and len(s) > 50]
        if quotes:
            digest["key_quotes"].append({
                "source_id": src.get("id"),
                "quotes": quotes[:3]
            })
    
    # Save digest
    digest_file = run_dir / "evidence-digest.md"
    digest_file.write_text(f"""# Evidence Digest

**Generated:** {digest['generated_at']}
**Sources analyzed:** {digest['source_count']}

## Top Claims

{json.dumps(digest['top_claims'], indent=2)}

## Key Quotes

{json.dumps(digest['key_quotes'], indent=2)}
""")
    
    return digest

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze research corpus")
    parser.add_argument("--run", help="Run directory")
    parser.add_argument("--sources", help="Sources JSON file")
    
    args = parser.parse_args()
    
    if args.run:
        run_dir = Path(args.run)
        sources_file = run_dir / "sources.json"
        
        if sources_file.exists():
            with open(sources_file) as f:
                sources = json.load(f)
            
            analysis = analyze_corpus(run_dir, sources)
            print(json.dumps(analysis, indent=2))
        else:
            print(f"No sources found in {run_dir}")
