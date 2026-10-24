<div align="center">

<img src="docs/assets/wordmark.svg" alt="AI Mood Board Studio" width="720" />

**Find inspiration. Organize references. Make an editable mood board.**

[Download for Mac](https://github.com/t0mAto1104/ai-moodboard-studio/releases/latest) · [简体中文](README.md) · [Changelog](CHANGELOG.md)

</div>

![The standalone desktop app](docs/ui-desktop-package.png)

A local-first visual research workspace built with React, Konva, FastAPI and SQLite. Search multiple image sources, save references with custom tags, optionally rank permitted images using local SigLIP 2 embeddings, and compose an editable canvas.

## Preview release

Version 0.2.0 is available as a ~317 MB DMG for Apple Silicon Macs. Drag the app into Applications; no separate Python or Node installation is needed. Target macOS 14+, tested on macOS 15.8.1 / M3 only. Intel and Windows packages are not provided.

The app is **ad-hoc signed, not Developer ID signed or notarized**. Other computers may block it. Formal distribution still needs signing, notarization and testing on additional machines. Do not disable system-wide security protections.

No model weights, developer API keys or existing user data are included. Each user configures their own accounts. Missing model weights fall back to metadata ranking.

## Workflow

1. Enable a source in Settings. For offline use, enable only the explicitly labeled demo source.
2. Enter a Chinese or English design brief and edit the resulting search plan if needed.
3. Browse results, inspect attribution and source permissions, and save references with tags.
4. Create a board from favorites or search results. Edit layouts with undo/redo, layers, locking, typography, color swatches and image replacement.
5. Save projects locally. Export permitted boards as PNG/PDF ZIPs containing attribution and a license manifest.

The demo source contains original procedural geometric fixtures, not real stock photographs or evidence of retrieval quality. Boards contain individually editable elements; they are not flattened AI-generated collages.

## AI and sources

Basic bilingual rules work without credentials. Optional cloud LLM parsing uses LiteLLM with user-configured OpenAI, Anthropic, Gemini, DeepSeek, Qwen, OpenRouter or compatible endpoints. No local LLM or Ollama is installed. Keys are stored by the backend in the OS keyring.

Optional vision uses `google/siglip2-base-patch16-224`, revision `75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2`, with normalized 768-dimensional embeddings. Select a separately prepared model folder in Settings; an external drive works. Loading is offline and selects CUDA, MPS or CPU. See [model setup](docs/model-setup.md).

Openverse, Art Institute of Chicago and The Met are available without keys; Unsplash and Pixabay require the user's own credentials. Providers can fail or rate-limit independently. Search access is not authorization to analyze, transform or export. Unknown/index-only rights cannot grant exports. Unsplash uses official hotlinks, attribution and download events; local ML analysis requires a separate user-confirmed authorization scope. Both stock sources support licensed creative-board PNG/PDF export with source manifests; Pixabay board previews use local copies rather than permanent hotlinks. No Pinterest scraping is used. See [source policy](docs/licenses.md).

## Prepare the optional vision model

Only SigLIP 2 Base is integrated. You can connect an existing complete folder, including `deployment_manifest.json`, in Settings. For a first download, get the [source ZIP](https://github.com/t0mAto1104/ai-moodboard-studio/archive/refs/heads/main.zip), open a terminal in its extracted root, and run:

```sh
python3.12 -m venv .model-tools
.model-tools/bin/python -m pip install 'huggingface_hub==0.36.2'
.model-tools/bin/python scripts/install_vision_model.py --directory '/Volumes/YOUR_DISK/AI_Models/siglip2-base-patch16-224'
```

Replace `YOUR_DISK` with your mounted drive name. The tool pins the revision, checks sizes and SHA256, generates the deployment manifest, and keeps weights / Hub caches on the selected disk. Reserve at least 3 GB (files total about 1.54 GB). Python is needed for this preparation step only; the desktop app bundles its runtime. No model weights are added to GitHub or the installer. [Model setup and read-only verification](docs/model-setup.md).

## Obtain image API credentials

| Source | Official entry point | What to enter |
| --- | --- | --- |
| Unsplash | [Developer portal](https://unsplash.com/developers) → Your apps → New Application → Keys | **Access Key**, not Secret Key |
| Pixabay | Sign in and open the [API documentation](https://pixabay.com/api/docs/) | Your **API Key** |
| Openverse | [Public API docs](https://docs.openverse.org/api/) | No key for the integrated anonymous path |
| Art Institute of Chicago | [Public API docs](https://api.artic.edu/docs/) | No key |
| The Met | [Public API docs](https://metmuseum.github.io/) | No key |

In Settings, save the key under the matching image source, enable it, and test the connection. Also select that source in the search menu. Unsplash currently documents 50 API calls/hour for Demo; Pixabay defaults to 100 calls/60 seconds, subject to account/response limits. These are requests, not image counts. Do not publish keys or confuse them with cloud LLM keys. [Step-by-step source guide](docs/image-api-setup.md).

## Run from source

Tested with Python 3.12 on macOS arm64. Vite 7 requires Node `^20.19.0 || >=22.12.0`.

```sh
git clone https://github.com/t0mAto1104/ai-moodboard-studio.git
cd ai-moodboard-studio
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-tested.txt
npm --prefix apps/web ci
npm --prefix apps/web run build
bash scripts/start.sh
```

Open http://127.0.0.1:8765. The server binds only to localhost. Stop with Ctrl+C. Environment variables can set `MOODBOARD_DATA_DIR` or an existing `SIGLIP_MODEL_DIR`; `.env` is not loaded automatically. Source data defaults to `.local`; desktop data defaults to `~/Library/Application Support/AI Mood Board Studio`. Their keyring service names are separate.

```sh
bash scripts/test.sh
# Optional real-model smoke test; metadata fallback fails this test:
.venv/bin/python scripts/smoke.py --vision --output /tmp/moodboard-vision.json
```

Recorded validation: 67 backend and 11 frontend tests; production build; standalone app startup/shutdown; read-only DMG relocation; project save/reopen; PNG/PDF with manifests; external-model CPU and MPS inference. This does not establish real-world retrieval accuracy, 10,000-image throughput or compatibility with every upstream service. [Validation](docs/validation.md) · [Performance](docs/performance.md) · [Known limitations](docs/known-limitations.md).

## Documentation

[User guide](docs/user-guide.md) · [Architecture](docs/architecture.md) · [REST API](docs/api.md) · [Desktop build](docs/desktop-packaging.md) · [Contributing](CONTRIBUTING.md).

No application source-code license has been selected yet. Public visibility alone does not grant a redistribution license. Third-party dependencies, models and images retain their respective terms. See [NOTICE](NOTICE.md).

## Favorites and editor

Create a board from 1–24 saved images across tags. The editor adds undo/redo, layers and locking, typography, shapes, alignment, keyboard shortcuts, favorites insertion and zoom. Styling, background and canvas ratio persist and export to PNG/PDF with source manifests. See [editor guide](docs/editor-guide.md) and [release validation](docs/release-0.2.0.md). Single-page boards only; grouping, collaboration and arbitrary crop focus are not implemented.
