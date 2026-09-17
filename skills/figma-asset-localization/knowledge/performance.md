# Performance Optimizations — Figma Asset Localization

Three mandatory optimizations reduce per-frame runtime from ~14 min to ~5 min (~64% faster).

## 1. Reuse EN Screenshot Across Locales
When processing multiple locales for the SAME parent asset:
- Export the EN screenshot ONCE for the first locale
- Save to `scripts/runs/EN_{asset_name}.png`
- Subsequent locales of the same asset reuse the cached file (skip Figma REST export + monday upload)
- Still upload to the monday Original Screenshot column per subitem, but from the cached file
- **Savings: ~195s per additional locale (20% of baseline)**

## 2. Batch Figma Text Writes
Instead of setting text one node at a time (10-15 separate Claude Code calls), batch ALL translations into a SINGLE Claude Code call:
- Pass all node IDs + translated text in one prompt
- Claude Code sets all text nodes in one MCP session
- Group up to 20 nodes per call; split into 2 calls only if >20 nodes
- **Savings: ~53s per frame (35% reduction in set_text time)**

Example prompt structure:
```
Using figma MCP (use_figma), set ALL these text translations on page '{loc_page}' frame '{frame_name}':
- nodeId1: 'Translated text 1'
- nodeId2: 'Translated text 2'
...(all nodes in one call)
```

## 3. Parallel Screenshot Uploads
Upload both screenshots (original EN + translated) to monday concurrently:
- Clear both file columns first (single GraphQL mutation)
- Fire both `add_file_to_column` uploads in parallel (background processes)
- Wait for both to complete
- **Savings: ~68s per frame (upload time cut in half)**

## When NOT to Optimize
- First locale for a new asset: must export EN screenshot (no cache yet)
- Re-runs (Part B): EN screenshot is already on the board, skip entirely
- Single-locale jobs: parallel uploads still apply, but reuse doesn't help

---

## Housekeeping (Mandatory After Every Run)

After each run completes (success or error), perform cleanup:

### Figma Cleanup
- **Verify page count:** Check that no duplicate locale pages were created
- If a duplicate was created accidentally, delete the newer one (higher node ID)
- Never leave orphan test pages in the Figma file
- **Never delete pages that weren't explicitly part of the current task**

### Deep Link Validation
- After ANY page operation (create, delete, rename), verify ALL board subitems' Figma Deep Link column
- Each `node-id` in the deep link must resolve to a frame on an active (non-deleted) page
- If a link points to a deleted or renamed page, update it to the correct node ID on the current page

### Local File Cleanup
- Remove temp files from `/tmp/` (glossary cache, upload results, Claude Code output)
- Keep only the final screenshot in `scripts/runs/` (delete intermediate/test screenshots)
- EN screenshot cache (`scripts/runs/EN_{asset}.png`) is retained for locale reuse

### Process Cleanup
- Verify no orphan Claude Code processes are running (`ps aux | grep claude`)
- Kill any stale processes from timed-out MCP calls

### Board Cleanup
- Verify both screenshot columns have exactly 1 file each (no stacking)
- Verify deep link resolves to the correct node on the loc page
- Verify reviewer column is populated
