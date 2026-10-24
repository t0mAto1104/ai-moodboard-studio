# Saved inspiration and manual downloads

The first navigation item is Home; projects remain the third item. Home opens the local inspiration library, not project creation. The header + still opens project creation.

Search cards offer 收藏, 设置标签 and either 下载 or 到来源下载. A direct favorite is ungrouped; the tag picker can create tags and assign multiple tags. Home filters 全部 / 未分组 / custom tags. Tags can be renamed/deleted; deleting a tag retains its photos and removes only that association. Removing a favorite retains the source asset and any projects. Refresh/reopen uses SQLite, not browser local storage.

Saving a favorite stores only asset reference, tag IDs and saved timestamp. Original source/creator/license links stay attached. Unsplash favorites use official hotlinks and visible photographer attribution. First saving a photo is treated as a selection/use event; it notifies download_location once. Editing tags or resaving the same favorite does not duplicate that event. Pixabay saved references do not permanently hotlink its temporary search-result preview.

## Individual download policy

| Source | Manual single-photo download |
|---|---|
| Unsplash | Allowed when the official API returned a trusted full image URL and valid download_location; event is sent per explicit download click |
| Pixabay | Allowed for official Content License API images and trusted returned image URLs; one user-triggered file at a time, no batch/mass download |
| Art Institute / Met | Allowed for verified public-domain material; image server access still applies |
| User upload / original demo | Allowed by existing declared rights / original fixture license |
| Openverse / unknown | Original-source rights not verified; open original source for review rather than treating indexed license text as authorization |

Individual download is separate from allowed_transform / allowed_export. The manual button itself does not grant new rights; official Unsplash/Pixabay stock licenses separately permit compliant creative-board exports. After download, subsequent use remains subject to the source license and third-party rights. API credentials never enter image links or returned files.

The backend rechecks policy on POST /api/assets/{id}/download, not from client-supplied booleans/URLs. It uses HTTPS host allowlists, public-IP validation/pinning, no redirects, 40MB cap, two simultaneous download slots, MIME and file signature checks. Full-resolution downloads are not decoded into giant pixel arrays on the backend. Bytes stream into bounded RAM, return as an attachment and are not saved in application image cache. Browser then saves the file at its download destination. SQLite keeps an audit record containing source, creator, license, filename and byte count. A failed tracking event blocks Unsplash file delivery and surfaces the error.

## Database/API

Migration 002 adds favorites, library_tags, download_records without changing existing project rows. Before the live migration a SQLite backup was made in .local/backups. New endpoints:

- GET /api/library
- POST /api/library/tags {name}
- PATCH /api/library/tags/{id} {name}
- DELETE /api/library/tags/{id}
- PUT /api/library/favorites/{asset_id} {tag_ids}
- DELETE /api/library/favorites/{asset_id}
- POST /api/assets/{asset_id}/download

## Official references checked 2026-10-24

- https://unsplash.com/license
- https://unsplash.com/documentation#track-a-photo-download
- https://help.unsplash.com/en/articles/2511258-guideline-triggering-a-download
- https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines
- https://pixabay.com/api/docs/
- https://pixabay.com/service/license-summary/
- https://api.artic.edu/docs/

These support ordinary user-triggered photo downloads, not mass ingestion, resale or unlimited downstream uses. No uncertain source has been auto-approved for download/export.
