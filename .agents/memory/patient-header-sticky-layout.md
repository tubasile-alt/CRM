---
name: Patient header sticky layout
description: The patient summary sits below the fixed navbar and must follow its measured height.
---

The prontuário patient summary should remain visible while scrolling, positioned below the fixed navigation bar. Its offset must use the navbar's measured height because the menu can wrap and change height across viewports.

**Why:** A fixed padding offset caused the published patient name to be covered by the blue navigation bar when its items wrapped.

**How to apply:** Keep the summary outside restrictive row containers, use `position: sticky`, and derive both content spacing and sticky offset from the current navbar height; include a compact mobile layout.