#!/bin/bash
# Install monday-presentation-v2 as a Claude Code skill

SKILL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CLAUDE_SKILLS="$HOME/.claude/skills"
SKILL_NAME="monday-presentation-v2"

mkdir -p "$CLAUDE_SKILLS"

if [ -L "$CLAUDE_SKILLS/$SKILL_NAME" ]; then
  rm "$CLAUDE_SKILLS/$SKILL_NAME"
fi

ln -sf "$SKILL_DIR" "$CLAUDE_SKILLS/$SKILL_NAME"

echo "✓ Skill installed: ~/.claude/skills/$SKILL_NAME"
echo "  Invoke with: /monday-presentation-v2"
