# Current source capabilities

| Source | Search / preview | Editable board | Pixel analysis / file export |
|---|---|---|---|
| Unsplash | Live verified with configured Access Key; official hotlinks and attribution | Saved reference board, official selection event | User-confirmed local-inference authorization enables RAM-only ranking; export remains disabled |
| Art Institute | Search live verified, official preview path | Supported for verified public-domain images when image fetch works | Current image server returns 403 to backend |
| Openverse | Live search and indexed thumbnails | Not enabled without source verification | Blocked until original-source rights verified |
| The Met | Adapter implemented; live search returns 403 | Public-domain path implemented | Depends on source access |
| Pixabay | Search/temporary preview adapter implemented; requires own key | Reference only | Contextual custom-license review pending |
| User uploads / demo | Verified local workflow | Supported | Permitted with declared rights / original demo license |

Settings enable a provider globally; search menu chooses among enabled/configured providers. Changing Settings immediately updates the menu. Empty selection yields a specific message. Connection tests consume an API request when uncached, so do not repeatedly test a demo key.

Official references checked during this change:
- https://unsplash.com/documentation
- https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines
- https://unsplash.com/api-terms (sections 6, 9, 12)
- https://pixabay.com/api/docs/

## Authorized local inference
The user explicitly confirmed permission covering local SigLIP encoding and ranking on 2026-10-24. The backend records a user declaration (not independent legal verification), scope `local_inference_only`. It enables temporary analysis, not image-file storage/transformation/export. Settings can disable analysis immediately. No grant is inferred from an Access Key.

Search now starts a separate /api/search/rank job for authorized images. RAM-only bytes → safe decode → SigLIP/color/quality/dedup → ranked metadata. Unsplash analysis renditions use 512×512 fit=max and preserve the official URL's ixid. Raw files and Unsplash vectors are not persistently cached. Model weights continue to load from the external disk.
