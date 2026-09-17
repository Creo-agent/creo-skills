# Figma Operations — Figma Asset Localization

## Access & Auth

- **Figma account:** nymeria-ai@monday.com (Full/expert seat on monday.com enterprise)
- **Figma editing:** ONLY via Claude Code + Figma MCP (`use_figma`). Never use Figma REST API for writes.
- **Figma REST API:** Read-only for metadata and screenshot export
  - Export: `GET https://api.figma.com/v1/images/{fileKey}?ids={nodeId}&format=png&scale=2`
  - Auth header credential: "Figma API Michael" (`WkMz2bZ8cx2lzgfJ`)
- **MCP config:** `claude mcp add --transport http --callback-port 19876 figma https://mcp.figma.com/mcp`
- **File must be shared with nymeria-ai@monday.com with Edit access**

## Claude Code Invocation
```bash
ANTHROPIC_API_KEY=<key> claude --permission-mode bypassPermissions --print "<prompt>"
```
Pass `ANTHROPIC_API_KEY` explicitly.

## Figma MCP Operation Sizing - MANDATORY

Each Figma MCP round-trip takes 5-15 seconds. Multi-step operations compound quickly.
- **Single node edit** (set text, change font): ~30-60s → timeout=120
- **3-5 node edits** in one call: ~2-3 min → timeout=300
- **Full asset translation** (10+ nodes + styles): break into multiple calls

**NEVER** send a single Claude Code call to do the full pipeline (translate + style + layout + screenshot). Instead:
1. Call 1: Set ALL text translations in a single batched call (up to 20 nodes per call; split into 2 calls only if >20 nodes)
2. Call 2: Apply style fixes (bold, list types)
3. Call 3: Layout fixes (font size, widths)
4. Screenshot via REST API (not Claude Code)

**Timeout rules:**
- Always set `timeout=120` minimum for any Figma MCP call
- For 5+ node edits: `timeout=300`
- Never use sub-agent spawns for Figma MCP work (too many layers of timeout). Use direct `exec` with Claude Code.
- If a call times out: the partial work is saved in Figma (writes are atomic per-node). Just continue from where it stopped.

## Figma MCP Re-authentication (self-service)
When Figma MCP auth expires mid-run (errors like `401 Unauthorized`, `token expired`, or `MCP connection failed`), do NOT flag it as a blocker. Re-authenticate yourself:
1. Start Claude Code interactively in tmux: `tmux new-session -d -s figma-auth; tmux send-keys -t figma-auth "claude" Enter`
2. Run `/mcp` → select figma → Authenticate
3. Open the OAuth URL in the agent's browser profile (`browser action=open profile=<agent_profile> url=<oauth_url>`)
4. Click "Agree & Allow Access" - use the agent's @monday.com account with Okta SSO credentials
5. Verify with `claude mcp list` → figma: Connected
6. Kill the tmux session: `tmux kill-session -t figma-auth`
7. Resume the localization job from where it stopped - do NOT restart from scratch

**Never** treat Figma MCP auth expiry as a pipeline error. Fix it and continue.

## Operation Sequence
1. Duplicate EN page → rename to `{Language} ({CODE}) AI` (e.g. `German (de-DE) AI`)
2. Extract text nodes via `use_figma` (flag brand, constrained, interactive, decorative)
3. Set translated text on duplicated page (preserve formatting, line count)
4. Font validation/swap for CJK/Cyrillic
5. Single layout pass (overflow resolution + asset-specific fixes)
6. Export original (EN) + translated screenshots via Figma REST API
7. Build deep link (`?node-id=...`)

## Deep Instance Extraction (mandatory)
The Figma REST API may NOT return text inside deeply nested component instances. The `use_figma` Plugin API with `findAll({type: 'TEXT'})` DOES reach them. Always use Plugin API for extraction — never rely solely on REST API depth traversal. Common missed nodes: column headers ("Owner", "Status"), view tabs ("Main table", "Table"), group headers ("This month", "Next month"), and status indicators ("Active", "Done", "In progress").

## Compound Node IDs Signal Deep Instances
Figma node IDs containing semicolons (e.g. `I281:1953618;4644:153936;10891:196227`) indicate text inside deeply nested component instances. These are invisible to REST API depth traversal but accessible via Plugin API `findAll({type: 'TEXT'})`.

**How to use:** When reviewing extracted text nodes, if ALL node IDs are simple (e.g. `123:456`), suspect that deep instances were missed. Re-extract using Plugin API and look for compound IDs.

## Page Management

**Page naming:** `{Language} ({CODE}) AI` (e.g. `German (de-DE) AI`, `Spanish (es-MX) AI`)

**Existing page handling:**
- FIRST: Search for an existing `{Language} ({CODE}) AI` page
- Also check for legacy names: `loc ({Language} {CODE})`, `loc ({Language} {CODE}) - {AssetName}`, or other variants
- **Housekeeping (mandatory):** After creating or reusing a loc page, check for any OTHER pages matching the same locale (old naming conventions, dated pages, POC-era duplicates). If found, verify they are NOT referenced by any board deep links, then delete them. This prevents page sprawl.
- If found (any naming variant) → reuse it. Rename to `{Language} ({CODE}) AI` if using a legacy name. Add the new asset frame to this page (duplicate only the frame, not the whole page)
- If NOT found → duplicate the entire EN source page, rename to `{Language} ({CODE}) AI`
- NEVER create a second page for the same locale under a different naming convention

**Cross-contamination prevention:** When reusing an existing loc page, verify the target frame belongs to the correct parent asset by checking node IDs. Do NOT translate a frame that belongs to a different parent asset.

## Figma Plugin API Notes
- `await figma.setCurrentPageAsync(page)` — `figma.currentPage = page` throws. Non-active pages have empty `children` until you switch.
- Direct MCP calls via JSON-RPC work when Claude Code auth is unavailable — extract OAuth token from `Claude Code-credentials` keychain entry.

## 🚨 SOURCE PAGE PROTECTION - ABSOLUTE RULE

**NEVER modify, translate, or write ANY text on the source (English) page.** This is a HARD STOP rule - zero tolerance.

- The source page contains the original EN frames. They are READ-ONLY.
- ALL localization work happens on DUPLICATED loc pages only.
- Before ANY Figma write operation (set_text, set_font, resize, etc.), the worker MUST verify the target node is on a localized page — NOT the source page.
- **Pre-write validation:** Extract the page name from the node's parent hierarchy. It must match a known loc page pattern: `{Language} ({CODE}) AI` or legacy `loc (...)`. If it matches NEITHER, ABORT the write immediately and report as `Error`.
- If a worker accidentally writes to the source page, it is a **pipeline-error** with immediate escalation to the WhatsApp group.

**Origin:** 2026-07-19 - Agent_builder_dark source page was contaminated with pt-BR translations. The worker translated directly on the English Source page instead of duplicating first. All text on the source frame was overwritten with Portuguese.
