#!/usr/bin/env python3
"""
hyperresearch-hermes — Pipeline de investigación profunda adaptado para Hermes

Uso:
    python research.py --query "tu pregunta" --tier full
    python research.py --query "comparar X vs Y" --tier light
    python research.py --resume <run-id>
"""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Paths
SKILL_DIR = Path(__file__).parent
VAULT_DIR = SKILL_DIR / "vault"
RUNS_DIR = SKILL_DIR / "runs"
VAULT_DB = VAULT_DIR / "sources.db"
DOCUMENTS_DIR = VAULT_DIR / "documents"

def init_vault():
    """Initialize SQLite vault if not exists"""
    import sqlite3
    
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(VAULT_DB)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id TEXT PRIMARY KEY,
            url TEXT UNIQUE,
            title TEXT,
            type TEXT,
            fetched_at TEXT,
            word_count INTEGER,
            topics TEXT,
            summary TEXT,
            file_path TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            query TEXT,
            tier TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT,
            manifest TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Vault initialized at {VAULT_DB}")

def create_run(query, tier="full"):
    """Create a new research run"""
    run_id = str(uuid.uuid4())[:8]
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Save query
    (run_dir / "query.md").write_text(f"# Research Query\n\n{query}\n\n---\n\n**Tier:** {tier}\n**Started:** {datetime.now().isoformat()}\n")
    
    # Register in DB
    import sqlite3
    conn = sqlite3.connect(VAULT_DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO runs (id, query, tier, status, created_at, updated_at) VALUES (?, ?, ?, 'active', ?, ?)",
        (run_id, query, tier, datetime.now().isoformat(), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    
    print(f"🚀 New run created: {run_id}")
    print(f"   Tier: {tier}")
    print(f"   Query: {query[:100]}...")
    print(f"   Directory: {run_dir}")
    
    return run_id

def main():
    parser = argparse.ArgumentParser(
        description="Hyperresearch-Hermes: Deep research pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python research.py --query "impact of AI on healthcare 2024" --tier full
  python research.py --query "compare React vs Vue" --tier light
  python research.py --resume abc12345
        """
    )
    
    parser.add_argument("--query", help="Research question")
    parser.add_argument("--tier", choices=["light", "full"], default="full", help="Research tier")
    parser.add_argument("--resume", help="Resume a previous run")
    parser.add_argument("--model", help="Model to use (default: from Hermes config)")
    parser.add_argument("--init", action="store_true", help="Initialize vault")
    
    args = parser.parse_args()
    
    # Init vault
    if args.init:
        init_vault()
        return
    
    # Resume run
    if args.resume:
        print(f"🔄 Resuming run: {args.resume}")
        run_dir = RUNS_DIR / args.resume
        if run_dir.exists():
            query = (run_dir / "query.md").read_text()
            print(f"   Query: {query[:200]}...")
            print("   (Implementation in progress)")
        else:
            print(f"   ❌ Run directory not found: {run_dir}")
        return
    
    # Create new run
    if args.query:
        run_id = create_run(args.query, args.tier)
        
        # TODO: Implement pipeline steps
        print("\n📋 Next steps:")
        print(f"   1. Run width sweep: python research.py --sweep {run_id}")
        print(f"   2. Run analysis: python research.py --analyze {run_id}")
        print(f"   3. Generate report: python research.py --synthesize {run_id}")
        return
    
    parser.print_help()

if __name__ == "__main__":
    main()
