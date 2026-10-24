# GitHub publication

Repository: https://github.com/t0mAto1104/ai-moodboard-studio

The source repository contains this application's directory contents at its root. Installer downloads live under Releases with SHA256 and installation instructions; model weights are never release assets.

## Preparing an update

Use a clean source checkout when possible. In a developer workspace containing private application data, first create a source-only snapshot using `scripts/prepare-publication.py NEW_DIRECTORY`, then run `scripts/check-publication.py NEW_DIRECTORY`. The exporter rejects an existing destination. It excludes environments, dependency trees, runtime data, model weights, installers, logs, private live reports and screenshots of third-party image collections. Public test JSON reports redact local username and drive paths. Review the actual diff as well: a pattern scan cannot prove arbitrary secrets are absent.

Run tests and review relative documentation links. Update CHANGELOG and release notes. Do not publish API keys, account-specific rights declarations, model files or users' boards/favorites. Credentials remain in OS keyring.

For a new installer, follow desktop-packaging.md. Re-run bundle audit, frozen self-test and disk-image integrity check. Upload the DMG, matching SHA256 and installation instructions as Release assets. Use an immutable release tag matching the reviewed commit; verify the remote asset size and SHA256 against the local file.

## Scope of the first publication

The initial local export Git checkout is `.publish/github-v0.1.0-final`, separate from the original parent workspace repository. That preserves the original model-deployment scripts and unrelated local files. Future changes in the development directory are not automatically committed or uploaded; explicitly export/review them or work in a normal clone of the public repository.

The project README is the project landing page. This publication does not modify the maintainer's personal GitHub profile README or account bio. No application source license was chosen as part of publishing; third-party component licenses remain separate.
