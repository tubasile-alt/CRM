---
name: Patient duplicate review
description: Duplicate candidate review policy for patient creation flows.
---

Weak name matches, including abbreviated names whose tokens are contained in a longer name, must be shown for review before a new patient is created. The user may explicitly confirm that none of the candidates is the same person; strong matches by exact identifiers remain blocked from direct creation.

**Why:** A patient with an abbreviated first-and-last name was created separately from an existing full-name record because a moderate similarity score was below the route's blocking threshold and was silently ignored.

**How to apply:** Use consistent candidate scoring across patient creation paths. Keep fuzzy names as review prompts rather than proof of identity, and require an explicit no-match confirmation before allowing a new record.
