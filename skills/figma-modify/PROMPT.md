# Figma Modify — Intake & Execution Workflow

## Pre-Flight: Ensure Figma Connection

Before anything else, verify the full Figma stack is ready. Run these checks in order and stop at the first failure:

### Check 1: Is the Figma plugin installed?
```bash
claude plugin list 2>/dev/null | grep -i figma
```
If missing, install it:
```bash
claude plugin install figma@claude-plugins-official
```
Then ask the user to restart Claude Code for the plugin to take effect.

### Check 2: Is Figma authenticated?
Look for `mcp__plugin_figma_figma__use_figma` in the available tools list. If the Figma MCP tools are not available:
1. Use ToolSearch to load the auth tools: `ToolSearch({ query: "select:mcp__plugin_figma_figma__authenticate,mcp__plugin_figma_figma__complete_authentication" })`
2. Call `mcp__plugin_figma_figma__authenticate` to start the OAuth flow
3. Present the auth URL to the user: "Please open this URL in your browser to connect Figma: [URL]"
4. Wait for confirmation. If redirect fails, ask: "Paste the full URL from your browser's address bar and I'll complete the connection."
5. Call `mcp__plugin_figma_figma__complete_authentication` with the pasted URL

### Check 3: Load the figma-use skill
This is MANDATORY before any `use_figma` call:
```
Skill({ skill: "figma:figma-use" })
```
This loads the Plugin API reference, type definitions, and critical gotchas. Without it, scripts will likely fail.

### Check 4: Load the Figma MCP tools
Use ToolSearch to load the tools you'll need:
```
ToolSearch({ query: "select:mcp__plugin_figma_figma__get_screenshot,mcp__plugin_figma_figma__get_metadata,mcp__plugin_figma_figma__use_figma,mcp__plugin_figma_figma__get_design_context" })
```

Once all 4 checks pass, proceed to Step 1.

---

## Step 1: Gather Context (ASK BEFORE DOING ANYTHING)

Before making any changes, ask the user these questions. Present them as a numbered list and wait for answers. Skip questions you can already answer from the user's message.

### Required Questions

1. **Which frame?** — "Can you share the Figma URL of the frame you want to modify? (or paste the link if you haven't already)"

2. **What changes?** — "What would you like to change? For example:"
   - Text content or styling (font, size, color, weight)
   - Colors or fills (background, element colors)
   - Layout or spacing (padding, gaps, alignment)
   - Resize to a new format (e.g., 1080x1920 for stories, 1200x628 for social)
   - Add, remove, or rearrange elements
   - Image or logo swaps

3. **Copy or in-place?** — "Should I modify the original frame, or create a copy with the changes?"

### Conditional Questions (ask only when relevant)

4. **If resizing:** "What are the target dimensions? (e.g., 1080x1920 for 9:16, 1920x1080 for 16:9)"

5. **If resizing:** "How should the layout adapt? Stack elements vertically, keep side-by-side, or let me decide what looks best?"

6. **If changing text:** "What should the new text say? (paste the exact content)"

7. **If changing colors:** "What are the new colors? (hex codes, or describe like 'make it darker')"

## Step 2: Inspect the Source Frame

ALWAYS do this before writing any changes. Run these in parallel:

```
get_metadata  → understand structure, hierarchy, node IDs
get_screenshot → see current visual state
```

For complex frames, also run:
```
get_design_context → get detailed styling info (fonts, colors, fills, layout properties)
```

From the inspection, note:
- All node IDs you'll need to reference
- Frame dimensions and layout mode (auto-layout vs absolute)
- Whether elements are components/instances or plain frames
- Text node IDs and their content
- Fill types (solid, gradient, image)
- Font families and styles used

## Step 3: Plan the Changes

Before executing, state your plan to the user in 2-3 sentences:
- What you'll change
- What you'll preserve
- Any design decisions you're making (e.g., "I'll stack the layout vertically and reduce font size to 48px to fit the narrower format")

Wait for user confirmation if the changes are significant (resizing, layout restructure). For small tweaks (text edit, color change), proceed directly.

## Step 4: Execute Changes

### Critical Rules for Figma Plugin API

Follow these rules to avoid the most common bugs:

#### Text Nodes
- **Creation order matters.** When creating text: load font → set fontName → set characters → `resize(width, height)` → `textAutoResize = "HEIGHT"` → appendChild to parent → `layoutSizingHorizontal = "FILL"`
- Skipping the resize step before setting textAutoResize causes 0-width text (every character on its own line)
- Always `await figma.loadFontAsync()` before ANY text property change
- For mixed styles: set the default font first, set characters, then use `setRangeFontName()` for bold/italic ranges
- Use `await figma.listAvailableFontsAsync()` if a font load fails — find the correct style name

#### Auto-Layout Frames
- After `resize()`, set `primaryAxisSizingMode = "FIXED"` if you want the frame to stay at that size (auto-layout defaults to HUG)
- `layoutSizingHorizontal/Vertical = 'FILL'` MUST be set AFTER `parent.appendChild(child)`
- `resize()` resets sizing modes to FIXED — call resize before setting HUG/FILL

#### Fills and Images
- Fills are read-only arrays — clone with `JSON.parse(JSON.stringify(node.fills))`, modify, then reassign
- Image fills can be cloned within the same file (imageHash stays valid)
- Colors use 0-1 range, not 0-255: `{r: 0.38, g: 0.38, b: 1}` not `{r: 97, g: 97, b: 255}`
- Paint `color` objects use `{r, g, b}` only — opacity goes at the paint level: `{ type: 'SOLID', color: {...}, opacity: 0.5 }`

#### Gradients
Common gradient transforms (2x3 matrix):
- **Top to bottom:** `[[6.12e-17, 1, 0], [-1, 6.12e-17, 1]]`
- **Left to right:** `[[1, 0, 0], [0, 1, 0]]`
- **Bottom to top:** `[[6.12e-17, -1, 1], [1, 6.12e-17, 0]]`

#### Cloning Elements
- Use `node.clone()` to duplicate elements (preserves all properties including image fills)
- Cloned nodes are added to the same parent — move them with `newParent.appendChild(clonedNode)`
- After cloning, resize with `node.resize(newWidth, newHeight)` if needed

#### Pages
- `figma.currentPage` resets to page 1 on each `use_figma` call
- Use `await figma.setCurrentPageAsync(page)` to switch (sync setter does NOT work)

#### Positioning
- New top-level nodes default to (0,0) — position them away from existing content
- Check `figma.currentPage.children` to find clear space (e.g., to the right of existing frames)

### Execution Pattern

Work in small incremental steps:

1. **Create structure first** — frames, auto-layout containers, positioning
2. **Validate** — `get_metadata` to check dimensions and hierarchy
3. **Add content** — text, clone icons/logos, set fills
4. **Validate** — `get_screenshot` to check visual result
5. **Fix issues** — adjust based on what you see
6. **Final screenshot** — confirm with user

NEVER try to do everything in one `use_figma` call. Break into 2-5 calls.

### Error Recovery

- `use_figma` is atomic — if it errors, NO changes were made. Safe to retry after fixing.
- On error: STOP, read the error, check file state with `get_metadata`, fix the script, then retry
- Common error "not implemented" = you used `figma.notify()` — remove it, use `return` instead

## Step 5: Present Result

After all changes are applied:

1. Take a final `get_screenshot`
2. Show it to the user
3. Briefly describe what was changed
4. Ask: "Does this look right, or would you like me to adjust anything?"

## Design Adaptation Cheatsheet (for resizing)

### 1:1 (1200x1200) → 9:16 (1080x1920) Story
- Stack horizontally-split layouts vertically (image top, content bottom)
- Keep font sizes similar or slightly reduce (the narrower width means more line wraps)
- Photo sections: ~40-45% of height, content: ~55-60%
- Use gradients at photo edges for smooth transitions

### 1:1 (1200x1200) → 16:9 (1920x1080) Landscape
- Expand horizontal layout — give more width to text areas
- Can increase font sizes slightly
- Side-by-side layouts work well at this ratio

### 16:9 → 9:16 (landscape to portrait)
- Usually requires complete layout restructure
- Stack all sections vertically
- Prioritize: what's most important goes at top/center

### Any → Square (1:1)
- Balance content visually in center
- Equal weight to image and text areas
- Consider 50/50 split or overlapping text on image
