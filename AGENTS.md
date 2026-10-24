# AI Mood Board Studio
- Local-first, algorithm-first. Preserve existing parent SigLIP deployment and all USB files.
- Python 3.12 FastAPI/SQLAlchemy; React/TypeScript/Vite/Konva frontend.
- No Ollama/local LLM. Cloud LLM via LiteLLM; rule parser works without credentials.
- Provider API fields must follow official documented contracts. No scraping Pinterest.
- License engine owns permissions. Unknown or unverified sources cannot be analyzed/stored/exported. Openverse index alone is not verification.
- Credentials only in OS keyring; never return secrets, log secrets, commit secrets or include in exports.
- Network/image limits and localhost protections apply to every path. No arbitrary URL fetch API.
- Test each milestone before adding the next. Do not claim mocked results as live results or algorithmic labels as human judgments.
- Commands from this directory: ../.venv/bin/python -m pytest apps/api/tests; npm --prefix apps/web test -- --run; npm --prefix apps/web run build; ./scripts/start.sh.
- Public checkout uses a local .venv; scripts/start.sh and scripts/test.sh prefer it, with compatibility fallback to the previous parent .venv. Use MOODBOARD_PYTHON to override.
- Backend owns normalized data, jobs, policy, ranking, layout, export. Frontend owns editing and presentation only, never authorizes export.
- Optional Qwen embedding and desktop packaging follow validated MVP. Different embedding versions never share vectors.

## Desktop packaging
Build only from the isolated `.build/venv`, using `desktop/requirements-build.txt`; mixing Anaconda system packages breaks PyInstaller hooks. Run `scripts/collect-package-notices.py`, `bash scripts/build-macos.sh`, standalone self-test on a fresh data directory, then `bash scripts/create-dmg.sh`. Explicit bundle data only; never bundle `.local`, keys, projects, model weights or model caches. `scripts/audit-bundle.py` must pass. Desktop data and keyring service stay separate from development. Verify native window startup/shutdown, optional external-model encoding, disk image integrity and relocation. Do not label an ad-hoc signed package as notarized. See docs/desktop-packaging.md.

## UI direction (user update)
Pure-white, Pinterest-like minimal workspace. Prefer icon rail, prominent search, image-first masonry. Remove nonessential secondary labels/descriptions, promotional copy, English eyebrow labels and redundant statuses. Keep accessible names and source/license information available in detail dialogs. Never scrape Pinterest; screenshot is a layout/style reference only.

## Library and individual downloads
Home is the first navigation destination; project management is separate. Favorites persist only links, tags and source metadata. Keep original-photo download permission separate from image storage, transformation and collage export. Unknown/index-only rights cannot be promoted to download rights. Unsplash selections/downloads must notify its official event endpoint without exposing credentials. No mass-download feature. Preserve attribution in search, Home and editor.

## GitHub publication
Canonical project: https://github.com/t0mAto1104/ai-moodboard-studio . Publish app-directory contents as repository root, not parent USB-deployment experiments. Use scripts/prepare-publication.py and scripts/check-publication.py for a fresh reviewable snapshot; private progress logs, live user reports and third-party image screenshots stay local. Installers belong to GitHub Releases, never Git history. No application source license has been selected: do not assign an open-source license without user authorization. See docs/github-publishing.md. The local first-publication Git checkout is .publish/github-v0.1.0-final, isolated from the original parent repository.
