# Contributing

This is an early preview. Read README.md, AGENTS.md and docs/architecture.md before changing code. The application source license has not been selected; discuss reuse or substantial contributions with the maintainer first.

## Local checks

Follow README setup, then run `bash scripts/test.sh`. New behavior needs meaningful tests at its owning boundary. Keep an explicit Mock path; tests should not need personal keys, paid calls, model downloads or network access. Visual integration tests are optional and must fail if actual inference was requested but only metadata ranking ran.

Backend owns source normalization, permission enforcement, jobs, ranking, geometry validation and export. Frontend owns presentation and editing; it cannot authorize restricted operations. Do not introduce Pinterest scraping, unsupported source fields or permission bypasses.

## Reports and pull requests

For bugs, include app version, OS / architecture, reproduction steps, expected behavior and a redacted error. Never post API keys, private project databases, images without publication rights or unredacted application logs.

Describe the concrete problem, change, validation and known limitations. Preserve existing projects, model directories and source provenance. Keep generated dependencies, build products, model weights and user data out of source commits. Installers belong in Releases, not Git history.

Desktop changes must also pass bundle audit, fresh-data frozen self-test and a native window startup/shutdown check. Do not claim a build is notarized unless it actually is.
