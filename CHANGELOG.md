# Changelog

## 0.2.0 — 2026-10-24

- Create editable boards directly from 1–24 favorites across custom tags, retaining every chosen image without AI re-selection.
- Add undo/redo, multi-selection actions, layers, locking, ordering, alignment, keyboard shortcuts and fit/zoom controls.
- Add text typography, rectangles/ellipses, background and ratio editing, image replacement, favorites insertion and uploads.
- Persist editor styling and render it in permission-checked PNG/PDF exports with attribution and license manifests.
- Preserve the existing white Studio design and navigation; no Canva integration or private templates.
- Add editor regression coverage and frozen-runtime tests. Existing projects use backward-compatible defaults.
- Publish a refreshed Apple Silicon desktop preview without model weights or user data; still ad-hoc signed, not notarized.

### Documentation and model preparation

- Add Chinese/English homepage instructions for fixed-version SigLIP setup and image API credential registration.
- Add an explicit model preparation CLI with pinned file hashes, external cache paths, safe resumption and read-only verification; five isolated tests passed. The desktop app still never auto-downloads weights.

## 0.1.2 — 2026-10-24

- Includes the 0.1.1 licensed stock export fix.
- Re-evaluate project-list thumbnails as well as the editor, so saved Pixabay references consistently use local previews.

## 0.1.1 — 2026-10-24

- Enable licensed Unsplash / Pixabay creative-board PNG/PDF exports, with complete attribution and manifests.
- Recompute existing project permissions on reopen; keep ML authorization separate from export rendering.
- Track unique Unsplash photos on every export; fail before delivery if tracking fails, without persisting original-image files.
- Serve saved Pixabay board images from local copies instead of permanent remote hotlinks; reject resize/crop-only single-image exports.
- Add stock export regressions and frozen-app self-tests. Unknown rights and unsafe URLs remain blocked.
- Publish an updated Apple Silicon installer, without model weights or private data. Still ad-hoc signed / not notarized.

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
