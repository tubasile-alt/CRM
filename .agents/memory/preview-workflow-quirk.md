---
name: Preview workflow orphan process
description: A stale Flask process can keep port 5000 occupied while the workflow appears running but the preview refuses connections.
---

When the Flask workflow reports running but the preview refuses connections, check both the actual listener and an HTTP request before changing application code. A stale process may need to be terminated so the workflow can start a clean instance.

**Why:** Restarting alone can leave an orphaned process holding port 5000, producing a misleading healthy workflow state and an unusable preview.

**How to apply:** Inspect workflow logs, listeners, and `curl` response; release the stale listener once, restart the workflow, and verify an actual page response.