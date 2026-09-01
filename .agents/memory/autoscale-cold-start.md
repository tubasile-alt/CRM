---
name: Autoscale cold-start readiness
description: Prevent Autoscale health checks from reaching Gunicorn before Flask finishes importing.
---

Gunicorn must preload this Flask application before opening its listening socket, and it must bind to the `PORT` supplied by the deployment environment.

**Why:** Gunicorn normally binds before workers finish importing the application. Cold imports of PDF, spreadsheet, and integration dependencies can exceed the Autoscale response window, so health checks repeatedly time out even though Gunicorn logs that it is listening.

**How to apply:** Keep deployment settings in a Gunicorn config with `preload_app = True` and derive `bind` from `PORT`. Validate changes with the exact production command and measure the first request, not only later warm requests.