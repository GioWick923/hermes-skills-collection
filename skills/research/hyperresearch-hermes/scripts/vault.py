#!/usr/bin/env python3
"""
vault.py — Gestión del vault de fuentes

El vault es una base de datos SQLite + archivos markdown que almacena
todas las fuentes investigadas. Es persistente entre runs.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
import json

VAULT_DIR = Path(__file__).parent.parent / "vault"
VAULT_DB = VAULT_DIR / "sources.db"
DOCUMENTS_DIR = VAULT_DIR / "documents"

def get_connection():
    """Get SQLite connection"""
    conn = sqlite3.connect(VAULT_DB)
    conn.row_factory = sqlite3.Row
    return conn

def add_source(url, title, content, source_type="article", topics=None):
    """Add a source to the vault"""
    conn = get_connection()
    c = conn.cursor()
    
    # Check if already exists
    c.execute("SELECT id FROM sources WHERE url = ?", (url,))
    existing = c.fetchone()
    
    if existing:
        print(f"⚠️  Source already exists: {url}")
        conn.close()
        return existing["id"]
    
    # Generate ID
    source_id = f"src_{len(list(c.execute('SELECT id FROM sources').fetchall())) + 1:04d}"
    
    # Save content to markdown file
    doc_path = DOCUMENTS_DIR / f"{source_id}.md"
    doc_path.write_text(f"""# {title}

**URL:** {url}
**Type:** {source_type}
**Fetched:** {datetime.now().isoformat()}
**Topics:** {', '.join(topics or [])}

---

{content}
""")
    
    # Insert into DB
    c.execute(
        """INSERT INTO sources 
           (id, url, title, type, fetched_at, word_count, topics, summary, file_path)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            source_id,
            url,
            title,
            source_type,
            datetime.now().isoformat(),
            len(content.split()),
            json.dumps(topics or []),
            content[:500] + "..." if len(content) > 500 else content,
            str(doc_path)
        )
    )
    
    conn.commit()
    conn.close()
    
    print(f"✅ Added source: {source_id} - {title[:50]}...")
    return source_id

def search_sources(query, limit=10):
    """Search sources by keyword"""
    conn = get_connection()
    c = conn.cursor()
    
    # Search in title and summary
    c.execute(
        """SELECT id, title, type, fetched_at, word_count, topics, summary
           FROM sources
           WHERE title LIKE ? OR summary LIKE ?
           ORDER BY fetched_at DESC
           LIMIT ?""",
        (f"%{query}%", f"%{query}%", limit)
    )
    
    results = []
    for row in c.fetchall():
        results.append({
            "id": row["id"],
            "title": row["title"],
            "type": row["type"],
            "fetched_at": row["fetched_at"],
            "word_count": row["word_count"],
            "topics": json.loads(row["topics"]) if row["topics"] else [],
            "summary": row["summary"]
        })
    
    conn.close()
    return results

def get_source(source_id):
    """Get a source by ID"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
    row = c.fetchone()
    
    if not row:
        return None
    
    # Read full content from file
    doc_path = Path(row["file_path"])
    content = doc_path.read_text() if doc_path.exists() else ""
    
    conn.close()
    
    return {
        **dict(row),
        "content": content
    }

def list_sources(limit=20):
    """List all sources"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""SELECT id, title, type, fetched_at, word_count 
                 FROM sources 
                 ORDER BY fetched_at DESC 
                 LIMIT ?""", (limit,))
    
    results = []
    for row in c.fetchall():
        results.append({
            "id": row["id"],
            "title": row["title"],
            "type": row["type"],
            "fetched_at": row["fetched_at"],
            "word_count": row["word_count"]
        })
    
    conn.close()
    return results

def get_stats():
    """Get vault statistics"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) as count FROM sources")
    total = c.fetchone()["count"]
    
    c.execute("SELECT type, COUNT(*) as count FROM sources GROUP BY type")
    by_type = {row["type"]: row["count"] for row in c.fetchall()}
    
    c.execute("SELECT SUM(word_count) as total FROM sources")
    total_words = c.fetchone()["total"] or 0
    
    conn.close()
    
    return {
        "total_sources": total,
        "by_type": by_type,
        "total_words": total_words
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Vault management")
    parser.add_argument("--search", help="Search sources")
    parser.add_argument("--get", help="Get source by ID")
    parser.add_argument("--list", action="store_true", help="List sources")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    
    args = parser.parse_args()
    
    if args.search:
        results = search_sources(args.search)
        print(f"Found {len(results)} sources:")
        for r in results:
            print(f"  [{r['id']}] {r['title']} ({r['word_count']} words)")
    
    elif args.get:
        source = get_source(args.get)
        if source:
            print(json.dumps(source, indent=2, default=str))
        else:
            print(f"Source not found: {args.get}")
    
    elif args.list:
        sources = list_sources()
        print(f"Total: {len(sources)} sources")
        for s in sources:
            print(f"  [{s['id']}] {s['title'][:50]}... ({s['word_count']} words)")
    
    elif args.stats:
        stats = get_stats()
        print("=== Vault Statistics ===")
        print(f"Total sources: {stats['total_sources']}")
        print(f"Total words: {stats['total_words']:,}")
        print("\nBy type:")
        for t, c in stats['by_type'].items():
            print(f"  {t}: {c}")
