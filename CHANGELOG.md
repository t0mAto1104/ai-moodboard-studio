# Changelog

## 0.1.0 — 2026-10-24

First public preview of AI Mood Board Studio.

- Pure-white local workspace with multi-source image search and bilingual intent parsing.
- Custom-tag inspiration library, grouped / ungrouped favorites and source attribution.
- Optional cloud LLM configuration through LiteLLM and OS keyring.
- Optional offline SigLIP 2 ranking, color analysis, quality checks, deduplication and MMR selection.
- Three editable Konva layouts, image replacement, color swatches, text and SQLite persistence.
- Permission-gated individual downloads and PNG/PDF ZIP export with attribution / license manifests.
- Standalone Apple Silicon macOS DMG; Python/runtime included, visual model weights excluded.
- Chinese / English project overview, setup guide, model connection guide and reproducible validation notes.

### Release limits

Ad-hoc signed only, not notarized. Tested on macOS 15.8.1 / M3; target macOS 14+. No Intel or Windows installer. Users provide their own keys and model files. No one-click model installer, auto-update or developer-data migration. Some upstream sources may return 403/rate limits. Qwen embedding and large-collection benchmarks remain future work. See docs/known-limitations.md.
