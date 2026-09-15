---
name: animation-to-webflow
description: >-
  Embed any standalone HTML/CSS/JS animation prototype into a live Webflow page.
  Covers the full pipeline: asset upload to Webflow CDN, bypassing Webflow's HTML
  sanitization via the JS DOM-builder pattern, scoped CSS, responsive scaling,
  trigger wiring (tabs, scroll, modal), and testing. Use whenever you have a local
  HTML animation file and need it live on a Webflow page — tab reveals, section
  entrances, hero loops, modal payloads. Encodes every non-obvious constraint
  discovered in production.
---

# Animation → Webflow

Take a standalone HTML/CSS/JS animation prototype and wire it into a live
Webflow page headlessly, using only the Webflow Data API. No Designer canvas
needed.

This skill exists because Webflow has several silent behaviors that cause
animations to appear broken, invisible, or partially rendered — with no error
message. Every constraint in `PROMPT.md` was discovered in production.

**Not for:** building a Webflow section from a Figma design from scratch — use
[`figma-to-webflow-section`](../figma-to-webflow-section/SKILL.md) for that.
This skill is specifically for embedding an *already-built* HTML/CSS/JS
animation file into an *existing* section.

For full parameter reference on any Webflow MCP tool used below
(`data_scripts_tool`, `data_assets_tool`, `data_sites_tool`, etc.), see
[`../../knowledge/webflow-mcp/tools-index.md`](../../knowledge/webflow-mcp/tools-index.md) —
every tool/action/required-param in one place.

---

## Quick-reference checklist

Run through this before writing a single line of code.

- [ ] Prototype opens and plays correctly in a plain browser?
- [ ] All assets (images, SVGs) are identified and will be uploaded to Webflow CDN
- [ ] Container element identified in Webflow DOM (by class or ID)
- [ ] Container has **explicit height CSS** — or a placeholder sibling does (see Phase 5)
- [ ] Trigger identified: tab click / scroll / load / modal open
- [ ] Unique ID chosen for the animation root element (`#section-anim-name`)
- [ ] Short CSS class prefix chosen (`xyz-`) — no collision with site CSS
- [ ] Unique `@keyframes` names chosen (prefix them too: `xyz-fadeIn`)
- [ ] `window.xyzPlay` and `window.xyzStop` API defined for trigger wiring

See **[`PROMPT.md`](PROMPT.md)** for the full 10-phase procedure, the
technical reference on what Webflow does to your code, and a common
failure-modes table.
