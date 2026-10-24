# Implementation plan and stage gates
1. Initialize API, DB migration, React shell, startup, health and basic tests. Gate: pytest + Vitest + production build + localhost HTTP.
2. Official Openverse/ArtIC/Met contracts, normalized schema, conservative policy, bounded search jobs, candidate grid, Mock. Gate: contract tests/errors/pagination and live low-volume smoke.
3. Bilingual rule parser and editable plan; LiteLLM settings/keyring/manual model registry/usage/fallback. Gate: schema and mocked cloud failures; no paid requests without configured user credentials.
4. Offline SigLIP integration, colors/quality/dedup/ranking/MMR, bounded processing/cache. Gate: algorithm tests + optional real-model smoke/benchmark.
5. Three layouts, Konva editing/replacement/colors/text, project persistence. Gate: geometry/persistence/UI tests and browser interaction.
6. Policy-gated PNG/PDF + manifests. Gate: allowed/denied tests and real artifact inspection.
7. Optional provider enhancements; evaluation templates and reproducible report. Qwen model download is not needed for MVP.

Each stage records commands, results, files and remaining limitations in docs/progress.md. No stage is complete merely because source files exist.
