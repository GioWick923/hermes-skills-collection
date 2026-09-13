---
name: hyperresearch-pipeline
description: "Pipeline de investigación profunda adaptado de hyperresearch para Hermes"
category: research
---

# Hyperresearch Pipeline (Hermes Edition)

Este skill orquesta el pipeline de investigación profunda usando subagentes Hermes.

## Pipeline Steps

### Step 1: Decompose
Descompone la query canónica en items atómicos.

**Entrada:** Query del usuario
**Salida:** Items atómicos + tier classification

**Prompt para subagente:**
```
You are a research decomposer. Break down this query into atomic research items:

Query: {query}

Return:
1. List of atomic research questions (5-10)
2. Coverage matrix (what each question covers)
3. Recommended tier: light or full
4. Search strategy per question
```

### Step 2: Width Sweep
Multi-perspective search + parallel fetching.

**Entrada:** Items atómicos
**Salida:** Corpus de fuentes en vault

**Prompt para subagente:**
```
You are a research fetcher. Execute the width sweep:

1. Search for each atomic question using multiple perspectives
2. Fetch top 5-10 sources per question (max 50 total)
3. Store each source in vault with metadata
4. Return corpus summary with source counts per topic
```

### Step 9: Evidence Digest
Top claims + verbatim quotes.

**Entrada:** Corpus de fuentes
**Salida:** evidence-digest.md

### Step 10: Triple Draft
3 parallel drafts from different angles.

**Entrada:** Corpus + analysis
**Salida:** 3 draft files

**Prompt para subagente (cada draft):**
```
You are a draft writer. Write a draft from {angle} perspective:

Guidelines:
- Use only cited sources
- Each claim must have a citation
- Highlight uncertainties
- Note contradictions found

Sources available: {source_list}
```

### Step 11: Synthesize
Plan + outline → final report.

**Entrada:** 3 drafts
**Salida:** final_report.md

### Step 12: Critics
4 adversarial critics in parallel.

**Prompt para cada crítico:**
```
You are a {critic_type} critic. Attack this draft:

Draft: {draft_content}

Your job:
- Find unsupported claims
- Identify missing counter-evidence
- Check for logical fallacies
- Flag potential biases

Return: findings JSON with severity levels
```

### Step 14.5: Cite-Check
Verify each citation supports its claim.

**Entrada:** Report + sources
**Salida:** Verification report

## Running the Pipeline

```bash
# Full pipeline
python scripts/research.py --query "your question" --tier full

# Or use individual steps
python scripts/research.py --step decompose --query "..."
python scripts/research.py --step sweep --items [...]
# ... etc
```

## Output Structure

```
runs/
└── <run-id>/
    ├── query.md           # Original query
    ├── corpus.md          # Corpus summary
    ├── analysis.json      # Analysis results
    ├── evidence-digest.md # Top claims & quotes
    ├── draft-1.md         # Draft from angle 1
    ├── draft-2.md         # Draft from angle 2
    ├── draft-3.md         # Draft from angle 3
    ├── critics.json       # Critic findings
    ├── final_report.md    # Final synthesized report
    └── sources.json       # Source list
```
