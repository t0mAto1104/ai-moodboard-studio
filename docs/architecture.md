# Architecture

Single local FastAPI process, SQLite with Alembic migrations, bounded background asyncio jobs, and React SPA. All services bind 127.0.0.1. Browser uses same-origin /api via Vite proxy during development and FastAPI static files in production.

## Boundaries
- Providers: async search(query, filters, page, per_page), normalize, details, usage policy and health. HTTPX bounded global/per-provider concurrency; finite retry/backoff. No implicit Mock fallback: explicit demo mode only.
- Policy: permissions are derived server-side from provenance, not client boolean fields. Museum public-domain records can be verified at source; Openverse index remains reference-only.
- Intent: Pydantic SearchIntent; cloud LLM settings and keyring; bounded invalid-output fallback to bilingual rules. No local LLM.
- Assets: persistent normalized metadata, separate licensed image cache, no storage for restricted media. Safe remote image access limited to supported provider hosts, public DNS, HTTPS and no redirects.
- Vision: lazy SigLIP singleton, controlled serialized batches, offline external model path, model/revision/preprocessor keyed vectors. Metadata fallback on missing model. No weight download.
- Pipeline: license gate -> bounded image decoding -> LAB/CIEDE2000, HSV, quality -> hash/visual duplicate checks -> normalized weighted ranking -> diversity selection.
- Layout: deterministic editorial/material/collage templates; normalized geometry validated server-side. Editable individual Konva nodes retain asset attribution.
- Export: server reloads asset permissions and sources, then renders PNG/PDF and attribution/license manifest. No client-supplied permission bypass.

## Contracts
SearchIntent: raw_prompt, subject, keywords/materials/colors/moods, palette, bounded queries, negatives, orientation/layout/count/language.
ImageAsset: provider identity, author/source/license evidence and operation permissions, image dimensions/URLs, ranking factors, embedding identity/hash and timestamps.
Project: id/name/prompt, intent, ratio/layout, linked assets and full editable layout. Jobs: queued/running/completed/failed/cancelled, progress/errors/result.

## Storage
Application data defaults to a project-local .local directory on internal disk (override MOODBOARD_DATA_DIR). Models stay at /Volumes/KINGSTON/AI_Models. SQLite contains normalized entity payloads and relational link tables. Separate cache/exports; cache cleanup never removes model weights or source files. Image blobs persisted only when policy allows.

## Known requirement conflict
The later cloud-LLM architecture supersedes legacy Ollama parser/settings/test bullets. Test cloud failure fallback instead. Human relevance judgments and retention metrics cannot be invented; evaluation scaffolding records unlabelled status until a person annotates.
