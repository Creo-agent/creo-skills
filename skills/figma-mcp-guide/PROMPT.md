# Figma MCP Guide — Usage Procedure

This skill is a passive reference, not an interactive workflow. It loads automatically when any
Figma task begins. Apply its rules silently; do not announce that the skill is active.

---

## When to Apply This Guide

Apply to **every task** that involves:
- A `figma.com` URL in the user's message
- Any mention of Figma (read, write, export, inspect, generate code from)
- Questions about the Figma MCP ("which tool should I use for X?")
- Any call to a `mcp__figma__*` or `mcp__e0cae42b__*` tool

---

## Tool Selection (run the decision tree from SKILL.md)

Before picking a Figma tool, always ask:

1. **Does this task WRITE to the canvas?** → `use_figma` (load `figma:figma-use` skill first, always)
2. **Does this need raw JSON / full node tree?** → `figma-rest: get_figma_data` (ToolSearch first)
3. **Does this need batch exports?** → `figma-rest: download_figma_images` (ToolSearch first)
4. **Otherwise** → use the quick-pick table in SKILL.md

Never guess the tool. The decision tree takes 2 seconds and prevents the most common class of failures.

---

## URL Handling (non-negotiable)

Every time a `figma.com` URL appears:

1. Extract `fileKey` — the segment after `/design/` or `/board/`
2. Extract `nodeId` — the `node-id` query param, with the **hyphen replaced by a colon**
   - URL: `node-id=47-1515` → API: `nodeId: "47:1515"`
3. For branch URLs, use the `branchKey` segment as the `fileKey`
4. If there is no `node-id`, omit `nodeId` entirely

Write this conversion explicitly in every tool call — never pass the raw URL param.

---

## Pre-Flight for use_figma

Before every single `use_figma` call:
```
Skill({ skill: "figma:figma-use" })
```
This is not optional. The skill provides Plugin API types, known gotchas, and behavior that
`use_figma` depends on. Calling `use_figma` without it causes silent and confusing failures.

---

## Handling Large Frames

If `get_design_context` might hit the token cap (full-page frame, many elements):

1. Run `get_metadata(fileKey)` first — inspect the layer tree
2. Find the specific sub-frame nodeId the user actually needs
3. Call `get_design_context` on that sub-frame, not the top-level frame

---

## Answering "Which Tool Should I Use?" Questions

When a user asks how to do something with Figma MCP, answer from the quick-pick table in SKILL.md.
Give the tool name, any prerequisite to load, and one-sentence rationale. Keep it to 3 lines or fewer.

Example:
> Q: "How do I read the design tokens from a Figma file?"
> A: Use `get_variable_defs(fileKey, nodeId)` — returns all variable values and token names
>    defined in the file. No prerequisite skill needed.

---

## After Export

When `download_assets` or `get_screenshot` returns a URL:
- Immediately `curl -sL -o "<filename>.<ext>" "<url>"` to save locally
- Never paste the URL into a reply as a link — it expires within seconds
- Confirm the file was saved before reporting success
