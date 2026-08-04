---
name: Deployment static asset cache
description: Published static assets may remain on an older build when a fixed query-string version is reused.
---

When a published page serves an older static JavaScript file than the current source, verify the served asset hash and change the asset query-string version before publishing again.

**Why:** The production receituário served the pre-merge JavaScript despite the published build being healthy; the preview had the newer code because the static asset version was unchanged.

**How to apply:** Treat a reused `?v=` value as a cache risk after frontend changes, especially when Service Workers or CDN caching are involved; use a new version identifier and republish.