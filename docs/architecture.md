# Architecture & Approach – AI Communication Assistant

## Problem
Support inboxes are crowded. Manual triage and drafting slow teams down. We automate retrieval, classification, prioritization, information extraction, and draft responses while keeping a human-in-the-loop for review.

## High-Level Design
1. **Ingestion (IMAP/Gmail/Outlook):** Fetch new emails; filter subjects containing Support/Query/Request/Help.
2. **Processing (FastAPI service):**
   - Sentiment (VADER): Positive/Neutral/Negative
   - Priority rules: urgent vs not_urgent (keywords like “immediately”, “critical”, “cannot access”)
   - Extraction: phones, alternate emails, basic metadata
   - RAG + Draft: retrieve KB snippets and generate an empathetic reply (OpenAI if available; otherwise fallback template)
3. **Storage (SQLite by default):** Emails, metadata, drafts, status (pending/resolved/replied).
4. **Dashboard (Next.js):** Sorted inbox (urgent first), message view, editable AI draft, send/resolve actions, analytics (24h stats, sentiment, priority).

## Flow
Email → Fetch → Analyze (sentiment/priority/extract) → RAG + Draft → Store → Dashboard (review/edit/send). APScheduler polls inbox periodically.

## Trade-offs
- Simple regex + VADER for speed; can be replaced with transformer models if needed.
- Lightweight RAG fallback (keyword retrieval) for offline demos.
- SQLite for simplicity; swap to Postgres in production.
