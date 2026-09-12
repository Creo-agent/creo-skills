---
name: resize-qa
description: |
  WHAT: Vision-based QA for Figma resize outputs. Runs after every resize or fix. Compares the output against the original master using screenshots, applies the full QA checklist, scores defects, and generates a structured report (what's good / what went wrong / actionable fixes).
  TRIGGERS: Called automatically by figma-resize after every use_figma change. Also invoked manually: "QA the resize", "review the output", "check the result".
  NOT FOR: General brand/design-system reviews → use design-review. Reviewing content changes → use design-review.
---

# Resize QA — Vision-Based Post-Resize Assessment

Runs after every resize operation or fix pass. Compares the output frame against the original master KV using Figma screenshots, applies the full scoring rubric, and generates a structured report.

## When to Run

- **Always:** after every `use_figma` write call in a resize session (whether first run or a fix pass).
- **Manually:** when the user says "QA this", "review the output", "how does it look", "check the result".

**NOT FOR:** General brand/design-system reviews → use `design-review`. Reviewing content changes → use `design-review`.

## What This Skill Produces

1. Both screenshots posted to the Slack thread (master + output side-by-side)
2. Technical checks (exact dimensions, font family)
3. Critical integrity pass (distortion, no-invention, text match, logo count)
4. Layer hygiene checks (off-canvas children, stacked layers, connector sides, branding containment, safe zones)
5. Layout placement checks (logo zone, CTA rules, visual container fidelity)
6. Safe zone and spacing measurements with pixel thresholds
7. Weighted defect score: starts at 100, deducts −100/−30/−10 per fatal/major/minor defect
8. 5-pillar vision inspection (Spacing & Structure, Color Fidelity, Typography, Crop Prevention, Spacing Structure)
9. Structured `VISION QA REPORT` saved to the deliverables folder and posted to Slack

## Invocation

```
Skill({ skill: "resize-qa" })
```

Apply the full workflow from PROMPT.md. Never skip or summarize — the structured report is the deliverable.

---

## Execution Workflow

See **PROMPT.md** for the complete step-by-step QA process, scoring rubric, vision inspection pillars, and report format.
