# Reproducible smoke benchmark — 2026-10-24

Same 8 procedural fixture images; select 6; isolated temporary DB; model revision 75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2. Model loaded from external USB; no weights downloaded. Each process starts cold. CPU and MPS runs occurred in different sandbox contexts, so this is a functional/device baseline, not a controlled speed contest.

| Mode | Generate seconds | Peak process RSS | MPS driver allocation at end |
|---|---:|---:|---:|
| Metadata | 0.155 | 144,556,032 bytes | N/A |
| SigLIP CPU | 42.010 | 1,224,015,872 bytes | N/A |
| SigLIP MPS | 86.956 | 540,573,696 bytes | 1,556,873,216 bytes |

All three completed search, selection, layout, persistence/reopen, relayout preserving image selection, and PNG/PDF exports with manifests. Both visual runs produced 8 valid 768-dimensional vectors in the recorded model space. PNG dimensions 1200×675 and white corner pixel were verified. Export stages each ~0.08–0.12 s.

Generation includes lazy model load, preprocessing and first-call device setup. No warmed throughput or 10,000-image estimate is claimed. MPS RSS alone excludes GPU/driver allocations; reported end allocation is not a measured peak. Do not sum these numbers as a rigorously measured total, due to unified memory and accounting differences.

Run scripts/smoke.py with or without --vision to reproduce. In this environment the restricted process detected only CPU; the authorized local process selected MPS. This demonstrates fallback and local acceleration separately. Real photo relevance and large-collection scaling require additional evaluation; human metrics are intentionally null.
