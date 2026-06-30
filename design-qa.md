# Chat Hub — Design QA

- Source visual truth: `artifacts/chat-hub-qa/reference-option-1.png`
- Implementation screenshot: `artifacts/chat-hub-qa/implementation-conversation.png`
- Focused comparison: `artifacts/chat-hub-qa/component-comparison.png`
- Viewport: 1488 × 1058 desktop
- State: prontuário aberto, drawer aberto e conversa selecionada

## Full-view comparison evidence

The current Clínica Basile prontuário remains structurally and visually unchanged. The implementation adds only the floating bell, Bootstrap backdrop and right-side conversation drawer. Opening the drawer keeps the same URL and preserves unsaved text in the active clinical textarea.

## Focused region comparison evidence

The focused side-by-side comparison checks the selected reference's drawer hierarchy against the implementation: compact conversation header, scrollable message area, incoming/outgoing bubble treatment and fixed composer. The implementation intentionally omits attachments, presence and patient-facing metadata because this first release is limited to the existing internal chat.

## Required fidelity surfaces

- Fonts and typography: inherits the application's Bootstrap font stack; hierarchy and compact UI sizing are consistent with the existing CRM.
- Spacing and layout rhythm: 420 px desktop drawer, full-width mobile rule, fixed composer and balanced 14–18 px internal spacing.
- Colors and visual tokens: existing CRM blue is retained for sent messages and actions; the green is isolated to the FAB.
- Image quality and assets: no new raster assets are required; existing Bootstrap Icons provide the bell, navigation and send icons.
- Copy and content: all labels are concise, in Portuguese and limited to internal conversations.

## Findings

No actionable P0, P1 or P2 mismatches remain.

## Patches made during QA

- Kept all hub IDs namespaced to avoid collisions with the full `/chat` screen.
- Preserved the clinical form value while opening and using the drawer.
- Prevented notification clicks from navigating away from the prontuário.
- Adjusted drawer height in preview mode so the environment banner does not cover the composer.
- Rendered contact names and messages with text nodes to avoid HTML injection.

## Follow-up polish

- P3: presence status, attachments and richer conversation metadata can be added in a future release if they become product requirements.

final result: passed
