---
name: figma-modify
description: |
  WHAT: Modify existing Figma designs in-place using the Figma MCP — text edits, color updates, layout restructuring, element add/remove, resizing to new formats.
  TRIGGERS: "change [something] in this Figma", "modify / tweak / adjust this design", "update the text / colors", "resize this frame to mobile", "adapt this layout", "fix the spacing", "move / swap / replace this element".
  NOT FOR: creating a new Figma file from scratch. Resizing a KV into all ad sizes natively → use figma-resize. Animating a Figma design → use figma-to-animation (in animations-and-motion-skills/).
---

# Figma Modify

Modify, tweak, and adapt existing Figma designs via the Figma MCP server. This skill handles all changes to existing designs — from small text edits to full layout restructuring for different formats.

## When This Skill Activates

Use when the user wants to:
- **Resize/adapt** a design to a different format (e.g., 1:1 to 9:16, desktop to mobile)
- **Tweak** colors, fonts, spacing, or sizing of existing elements
- **Edit** text content in a Figma frame
- **Rearrange** layout or move elements around
- **Add or remove** elements from an existing design
- **Duplicate and modify** a frame with changes
- **Update** a design to match new brand guidelines

Keywords: "change", "modify", "tweak", "adjust", "resize", "adapt", "update", "edit", "fix", "move", "swap", "replace", "reformat"

## Setup & Dependencies

This skill depends on the Figma MCP plugin and the `figma:figma-use` skill. Before doing any work, follow this setup sequence:

### Step 0: Verify Figma Plugin Installation

Check if the Figma plugin is installed:
```bash
claude plugin list 2>/dev/null | grep -i figma
```

**If NOT installed**, install it:
```bash
claude plugin install figma@claude-plugins-official
```

### Step 1: Authenticate with Figma

Check if the Figma MCP tools are available (look for `mcp__plugin_figma_figma__use_figma` in available tools). If not:

1. Call `mcp__plugin_figma_figma__authenticate` to start the OAuth flow
2. Present the auth URL to the user and ask them to open it in their browser
3. Wait for the user to confirm authentication is complete
4. If the redirect page shows a connection error, ask the user to paste the full callback URL and call `mcp__plugin_figma_figma__complete_authentication` with it

### Step 2: Load the figma-use Skill

**MANDATORY before ANY `use_figma` call.** Always load the `figma:figma-use` skill first:

```
Skill({ skill: "figma:figma-use" })
```

This provides the Plugin API reference, gotchas, and type definitions. Without it, `use_figma` calls are likely to fail with hard-to-debug errors.

### Dependency Chain Summary

```
figma-modify (this skill)
  ├── Figma plugin installed (claude plugin install figma@claude-plugins-official)
  ├── Figma authenticated (OAuth flow via authenticate tool)
  └── figma:figma-use skill loaded (MUST load before every use_figma call)
```

## Workflow

See PROMPT.md for the full intake questionnaire and execution workflow.
