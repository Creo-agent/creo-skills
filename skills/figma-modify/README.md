# Figma Modify — Claude Code Skill

A Claude Code skill for modifying, tweaking, resizing, and adapting existing Figma designs using the Figma MCP server.

Instead of manually editing designs in Figma, describe what you want changed and Claude will do it — text edits, color updates, layout restructuring, resizing to new formats, and more.

## What It Does

- **Resize/adapt** designs between formats (1:1 to 9:16, desktop to mobile, etc.)
- **Tweak** colors, fonts, spacing, or sizing of existing elements
- **Edit** text content directly in Figma frames
- **Rearrange** layout or move elements around
- **Add or remove** elements from an existing design
- **Duplicate and modify** frames with changes

## How It Works

When triggered, the skill:
1. **Sets up the Figma connection** — installs the Figma plugin, handles OAuth authentication, and loads required dependencies
2. **Asks clarifying questions** — what frame, what changes, copy or in-place, target dimensions, etc.
3. **Inspects the design** — screenshots and metadata before touching anything
4. **Executes changes incrementally** — small steps with visual validation between each
5. **Presents the result** — final screenshot for your approval

## Install

### One-liner

```bash
git clone https://github.com/eliorsi-hash/figma-modify.git ~/.claude/skills/figma-modify
```

### Manual

1. Download `SKILL.md` and `PROMPT.md` from this repo
2. Create the directory `~/.claude/skills/figma-modify/`
3. Place both files inside it

### Verify

Restart Claude Code (or start a new session), then type `/figma-modify` — it should appear in the skills list.

## Prerequisites

This skill requires the **Figma MCP plugin** for Claude Code. The skill will walk you through installation automatically, but if you want to set it up beforehand:

```bash
claude plugin install figma@claude-plugins-official
```

On first use, you'll be prompted to authenticate with Figma via OAuth in your browser.

## Usage

### Option 1: Slash command
Type `/figma-modify` in Claude Code to trigger the skill directly.

### Option 2: Natural language
Just describe what you want — the skill auto-triggers on keywords like "change", "modify", "tweak", "resize", "adapt", "update", "edit", "fix", "move", "swap", "replace", or "reformat" when referring to a Figma design.

### Examples

```
# Resize a design for Instagram Stories
"Resize this Figma frame to 9:16 for stories: https://figma.com/design/..."

# Change text content
"Update the headline in this frame to say 'New Product Launch': https://figma.com/design/..."

# Tweak colors
"Make the background darker and change the text to white: https://figma.com/design/..."

# Adapt layout
"Rearrange this horizontal layout to stack vertically for mobile: https://figma.com/design/..."
```

## What's Inside

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill metadata, trigger conditions, and setup/dependency chain |
| `PROMPT.md` | Full workflow: intake questions, Plugin API gotchas, execution patterns, design adaptation cheatsheet |

## Key Features in the Skill

- **Intake questionnaire** — asks the right questions before making changes
- **Auto-setup** — handles Figma plugin installation, OAuth, and skill dependencies
- **Plugin API gotchas** — encodes hard-won knowledge about text node creation order, auto-layout sizing, fill cloning, gradient transforms, and more
- **Incremental execution** — never tries to do everything in one script call; validates with screenshots between steps
- **Design adaptation cheatsheet** — common patterns for converting between aspect ratios (1:1, 9:16, 16:9)

## Uninstall

```bash
rm -rf ~/.claude/skills/figma-modify
```

## License

MIT
