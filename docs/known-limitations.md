# Known limitations and next work

- Historical low-volume checks: Unsplash search/preview/reference-board worked with configured credentials; ArtIC/Openverse metadata and trusted previews worked. ArtIC backend image retrieval and Met search returned HTTP 403. Re-test with your own account and network; these are not uptime guarantees. Mock/uploads provide export-capable workflows.
- No paid cloud account/API keys supplied; error paths and schema validation are tested, but live cloud provider compatibility must be checked with user-configured credentials.
- Evaluation prompts can be prepared; genuine human relevance judgments/retention rates cannot be invented. Precision@10/NDCG@10 require labeled data. Benchmark timing is not relevance evidence.
- Qwen3-VL embedding is optional and not implemented/downloaded. Only SigLIP 2 is available.
- JSON-backed SQLAlchemy tables have application-level links rather than SQL foreign-key constraints. Migrations exist; stronger relational integrity and stale link cleanup remain work.
- Layouts are deterministic editable templates; no learned focal-point crop detection. Contain mode defaults to avoiding unwanted cropping.
- Ranking uses greedy MMR, basic source/query diversity and heuristic weights, not a fully constrained global optimizer.
- Individual image inference is bounded and memory-conscious; bulk batching and 10k-image throughput profiling remain work.
- Search and inference sorting scores are not calibrated relevance probabilities. Cache and preprocessing revisions prevent vector-space mixing.
- Unsplash reference boards are editable/savable; the user-authorized local-inference option permits RAM-only visual ranking. Licensed creative-board PNG/PDF export is supported independently from ML authorization. Authorization is recorded as user-declared, not independently verified. Pixabay supports licensed creative-board export and locally cached board previews; single-image resize/crop-only exports are rejected. Each user supplies their own key.
- Runtime package versions are recorded for this Mac; other operating systems not verified. Vite emits a bundle-size warning; test tooling emits an upstream httpx deprecation warning.
- Desktop release is ad-hoc signed, not Developer ID signed/notarized. Only the recorded Apple Silicon/macOS host was tested; no Intel/Windows package, automatic updates or automatic migration from developer data.
- No in-app one-click model installer yet. The opt-in scripts/install_vision_model.py CLI now prepares and verifies the supported fixed-version model folder and manifest; the app never silently downloads weights.
