# Resize QA — Vision-Based Post-Resize Assessment

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that scores Figma resize outputs against the original master. Companion skill to `figma-resize` — runs automatically after every `use_figma` write call in a resize session.

## What It Does

1. Captures screenshots of both the original master and the output frame via Figma MCP
2. Posts both images to the Slack thread for side-by-side comparison
3. Runs technical checks (exact dimensions, font family verification)
4. Applies critical integrity checks (distortion, no-invention, text match, logo count)
5. Runs layer hygiene checks from layer data: off-canvas children, stacked layers, texture coverage, connector side, branding containment, platform safe zones, horizontal alignment drift, corner radius proportionality
6. Checks element placement (logo zone, CTA rules, visual container fidelity)
7. Measures safe zones and spacing with pixel thresholds
8. Scores the output on a 100-point weighted defect scale
9. Runs a 5-pillar visual inspection from the screenshots
10. Posts a structured VISION QA REPORT (wins, defects by pillar, exact fix instructions)
11. Saves the report to the deliverables folder

## Scoring Rubric

| Defect Type | Deduction |
|-------------|-----------|
| Fatal (wrong dimensions, distortion, text changed, wrong font, added elements) | −100 pts each |
| Major (logo/CTA on edges, container styling lost, safe zone violation, ghost button, off-canvas children, connector on wrong side, branding overflow) | −30 pts each |
| Minor (spacing below minimum, crowding, brand name line-break, stacked texture layers, texture not covering content area, alignment drift, corner radius not scaled) | −10 pts each |

| Score | Verdict |
|-------|---------|
| 100 | Perfect Pass — ship immediately |
| 80–99 | Conditional Pass — fix spacing only |
| ≤79 | Fail / Reject — full correction required |

## 5 Vision Pillars

1. **Spacing & Structure** — intentional composition, reading order, balanced margins
2. **Color Fidelity & Contrast** — background extension matches master, CTA contrast readable
3. **Typography & Hierarchy** — Poppins only, headline dominant, brand names unbroken
4. **Crop Prevention** — no clipped descenders, visual subject fully visible
5. **Spacing Structure** — no crowding, CTA clear space, safe zones empty

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- [Figma MCP plugin](https://www.figma.com/community/plugin/claude-code-figma) connected and running
- Both the original master node ID and output frame node ID available in session context (captured by `figma-resize` before running)

## Installation

Install alongside `figma-resize`:

```bash
cp -r resize-qa ~/.claude/skills/
```

## Usage

Invoked automatically by `figma-resize` after every write. To invoke manually:

```
/resize-qa
```

Or describe what you want:
- "QA the resize"
- "Review the output"
- "How does it look?"

## File Structure

```
resize-qa/
  SKILL.md    — Frontmatter, when/what, invocation
  PROMPT.md   — Full QA workflow, scoring rubric, 5-pillar vision inspection, report format
  README.md   — This file
```

## License

MIT
