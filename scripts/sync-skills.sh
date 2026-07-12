#!/usr/bin/env bash
# sync-skills.sh — Check DaPulse/marketing-design-ai-hub for new/updated skills
# and install them to ~/.claude/skills/ + Creo Workspace skills/ wrappers.
# Run daily by Creo's cron. Opens a GitHub PR on Creo-agent/creo-skills if anything changed.

set -euo pipefail

HUB_REPO="https://github.com/DaPulse/marketing-design-ai-hub.git"
HUB_SKILLS_DIR="skills"
INSTALL_DIR="$HOME/.claude/skills"
CREO_SKILLS_DIR="/Users/creativeagent/Creative Operations/Creo Workspace/skills"
REGISTRY_REPO="https://github.com/Creo-agent/creo-skills.git"
WORK_DIR="/tmp/mdai-hub-sync-$$"
REGISTRY_WORK="/tmp/creo-skills-sync-$$"
DATE=$(date +%Y-%m-%d)
BRANCH="skill-sync/$DATE"

echo "[sync-skills] Starting at $(date)"

# ── 1. Pull latest from hub ────────────────────────────────────────────────
echo "[sync-skills] Fetching hub..."
if [ -d /tmp/mdai-hub-install/.git ]; then
  cd /tmp/mdai-hub-install && git pull --quiet
  WORK_DIR=/tmp/mdai-hub-install
else
  git clone --filter=blob:none --sparse "$HUB_REPO" "$WORK_DIR" 2>/dev/null
  cd "$WORK_DIR"
  git sparse-checkout set "$HUB_SKILLS_DIR"
  git checkout --quiet
fi

cd "$WORK_DIR"

# ── 2. Discover skills ────────────────────────────────────────────────────
SKILLS=()
for d in "$HUB_SKILLS_DIR"/*/; do
  skill=$(basename "$d")
  SKILLS+=("$skill")
done

echo "[sync-skills] Found ${#SKILLS[@]} skills in hub: ${SKILLS[*]}"

# ── 3. Compare and collect changes ───────────────────────────────────────
CHANGED=()
for skill in "${SKILLS[@]}"; do
  src="$HUB_SKILLS_DIR/$skill/SKILL.md"
  dst="$INSTALL_DIR/$skill/SKILL.md"
  if [ ! -f "$dst" ]; then
    echo "  NEW: $skill"
    CHANGED+=("$skill")
  elif ! diff -q "$src" "$dst" > /dev/null 2>&1; then
    echo "  CHANGED: $skill"
    CHANGED+=("$skill")
  else
    # Check PROMPT.md too
    src_p="$HUB_SKILLS_DIR/$skill/PROMPT.md"
    dst_p="$INSTALL_DIR/$skill/PROMPT.md"
    if [ -f "$src_p" ] && [ -f "$dst_p" ] && ! diff -q "$src_p" "$dst_p" > /dev/null 2>&1; then
      echo "  CHANGED (PROMPT.md): $skill"
      CHANGED+=("$skill")
    fi
  fi
done

if [ ${#CHANGED[@]} -eq 0 ]; then
  echo "[sync-skills] All skills up to date. Nothing to do."
  exit 0
fi

echo "[sync-skills] ${#CHANGED[@]} skill(s) need update: ${CHANGED[*]}"

# ── 4. Install changed skills ─────────────────────────────────────────────
for skill in "${CHANGED[@]}"; do
  echo "  Installing $skill → $INSTALL_DIR/$skill"
  rm -rf "$INSTALL_DIR/$skill"
  cp -r "$HUB_SKILLS_DIR/$skill" "$INSTALL_DIR/$skill"

  # Regenerate Creo wrapper
  wrapper="$CREO_SKILLS_DIR/$skill.md"
  skill_md="$INSTALL_DIR/$skill/SKILL.md"
  prompt_md="$INSTALL_DIR/$skill/PROMPT.md"
  {
    cat "$skill_md"
    if [ -f "$prompt_md" ]; then
      echo ""
      echo "---"
      echo ""
      cat "$prompt_md"
    fi
    echo ""
    echo "---"
    echo "_Full skill installed at \`~/.claude/skills/$skill/\`. Supporting files are available there._"
  } > "$wrapper"
  echo "  Wrapper updated: $wrapper"
done

# ── 5. Clone registry repo, create branch, commit, push, open PR ──────────
echo "[sync-skills] Opening PR on Creo-agent/creo-skills..."

git clone "$REGISTRY_REPO" "$REGISTRY_WORK" 2>/dev/null
cd "$REGISTRY_WORK"
git config user.name "Creo-agent"
git config user.email "creo@monday.com"
git checkout -b "$BRANCH"

# Copy updated skill dirs into registry
for skill in "${CHANGED[@]}"; do
  rm -rf "skills/$skill"
  cp -r "$WORK_DIR/$HUB_SKILLS_DIR/$skill" "skills/$skill"
done

# Update README status table (mark all known skills as installed)
# (Simple sed — keeps the table rows intact, just ensures ✅ installed)
git add skills/
git commit -m "skill-sync: update ${CHANGED[*]} ($DATE)"
git push origin "$BRANCH"

PR_BODY="Automated skill sync from \`DaPulse/marketing-design-ai-hub\` on $DATE.

**Changed skills:**
$(printf -- '- %s\n' "${CHANGED[@]}")

After merging, these skills will be active on the next Creo session.
Skills were already installed to \`~/.claude/skills/\` and Creo Workspace wrappers were updated."

gh pr create \
  --repo Creo-agent/creo-skills \
  --head "$BRANCH" \
  --base main \
  --title "Skill sync: ${CHANGED[*]} ($DATE)" \
  --body "$PR_BODY"

echo "[sync-skills] PR created. Done."
