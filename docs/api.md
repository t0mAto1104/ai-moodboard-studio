# Local API

Base URL: http://127.0.0.1:8765/api. Generated complete schema: /openapi.json, interactive docs: /docs.
Mutating requests require `X-Moodboard-Request: 1`; foreign Origin/Host rejected. JSON by default, upload uses multipart. Bind only localhost; not a multiuser authenticated public service.

| Route | Purpose |
|---|---|
| GET /health | Database/service health |
| GET /providers | Availability and policy |
| PUT /providers/{name}/settings | enabled and optional api_key; keyring only |
| POST /providers/{name}/health | Low-volume provider diagnostic |
| POST /intent/parse | {prompt}; validated intent and cloud/rules mode |
| POST /search | queries, providers, page, per_page, commercial; job_id |
| POST /search/rank | asset_ids, intent, preference, commercial; policy-gated RAM-only visual analysis job |
| GET /jobs/{id} | queued/running/completed/failed/cancelled, progress, result, error |
| POST /jobs/{id}/cancel | Cancel pending/running job |
| POST /assets/upload | file + rights_confirmed=true |
| GET /assets/{id}/image | Policy-gated image bytes |
| POST /projects | name, intent, asset_ids, ratio, layout_style, commercial |
| GET /projects, /projects/{id} | List/reopen |
| PATCH /projects/{id} | Save validated geometry and associations |
| DELETE /projects/{id} | Remove project |
| POST /projects/{id}/duplicate | Copy project |
| POST /projects/{id}/generate | preference, use_vision, relayout_only; job_id |
| POST /projects/{id}/export | format png/pdf; job_id |
| GET /exports/{id} | Authorized export ZIP |
| GET/PUT /llm/settings | Configuration, never return secret |
| GET /llm/models, /llm/usage | Registry / token and estimated usage |
| POST /llm/test | Real connection and schema validation |
| GET /system | Model path availability/device/cache |
| PUT /system/model/directory | Validate and connect an existing fixed-version model directory |
| POST /system/model/select | Native desktop folder picker; unsupported in browser-only mode |
| POST /system/cache/clear | Remove image cache only |

Jobs interrupted by process restart become failed with a retry message. Inference already dispatched to a thread can finish after cancellation, but cancelled job status remains terminal. SQLite is local single-process storage, not a distributed job queue.

Provider settings accept optional analysis_enabled and analysis_rights_confirmed for Unsplash. Enabling without a prior or current rights declaration is rejected. This grants local inference only, not storage/export.
