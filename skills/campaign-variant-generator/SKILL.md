---
name: campaign-variant-generator
description: Reference for the Campaign Variant Generator Figma plugin (generates ad headline/CTA variants via n8n + Claude). Not directly executable — runs via Figma plugin. Use when asked about variant generation architecture or campaign asset modification.
---

# Skill: Campaign Variant Generator (Reference)

**Domain:** Localization
**Owner:** michael@monday.com (Michael Eizenstat)

## When to Use
- Questions about how the campaign variant generator works
- Understanding the Figma plugin → n8n → Claude pipeline
- Debugging variant generation issues

## Architecture

```
Figma Plugin (CM's browser)
  ↓ POST + HMAC-SHA256
n8n Webhook (campaign-variants)
  → Load brief from Google Docs
  → Build prompt (brief + forbidden phrases + layer specs)
  → Claude call (7 coherent variant sets)
  → Validate schema + filter forbidden phrases
  ↓ JSON response
Figma Plugin
  → Pixel-test each set against actual fonts
  → Display valid sets → CM picks one
  → Apply to duplicate frame on new page
```

## Plugin Modes
1. **Edit Mode** — CM edits text layers inline with live pixel-fit indicator
2. **Variant Mode** — Generate N variant sets via Claude, pixel-filter, apply chosen set
3. **Export Mode** — PNG download or Cloudinary upload

## Key Components
- **Brief:** Google Doc `11Ofg3zGxBHMYVORdlMJgLlq62fTjC9vMbx_CI9BOPBw`
- **Forbidden phrases:** `campaign/docs/forbidden-phrases.json`
- **Four Tenets:** Use case clarity, Customer-centricity, Crown the person not AI, Highlight the possible
- **Pixel validation:** Done in-plugin (n8n can't render fonts)
- **HMAC auth:** Plugin signs requests, n8n verifies

## Brand Rules
All variants must follow `../../knowledge/brand-rules.md`:
- monday.com always lowercase
- "Create" not "Build" your own agent
- "people" not "humans"
- Crown the person, not AI

## Related
- [Brand Rules](../../knowledge/brand-rules.md)
- [Figma Asset Localization](../figma-asset-localization/SKILL.md)
