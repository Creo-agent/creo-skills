---
name: resize-qa
description: Vision-based QA for Figma resize outputs. Runs automatically after every use_figma write call in a figma-resize session, and can be invoked manually. Captures screenshots of both the original master and the output, applies a full weighted scoring rubric (100-point scale), runs a 5-pillar vision inspection, and posts a structured VISION QA REPORT with wins, defects by pillar, and exact fix instructions.
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
4. Layout placement checks (logo zone, CTA rules, visual container fidelity)
5. Safe zone and spacing measurements with pixel thresholds
6. Weighted defect score: starts at 100, deducts −100/−30/−10 per fatal/major/minor defect
7. 5-pillar vision inspection (Spacing & Structure, Color Fidelity, Typography, Crop Prevention, Spacing Structure)
8. Structured `VISION QA REPORT` saved to the deliverables folder and posted to Slack

## Invocation

```
Skill({ skill: "resize-qa" })
```

Apply the full workflow from PROMPT.md. Never skip or summarize — the structured report is the deliverable.

---

## Execution Workflow

See **PROMPT.md** for the complete step-by-step QA process, scoring rubric, vision inspection pillars, and report format.
