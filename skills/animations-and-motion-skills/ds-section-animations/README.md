# DS Section Animations

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that adds motion and
interactivity to Clay Design System section stories using **native browser APIs** (CSS + vanilla
JS) — the DS does not use Framer Motion, so this skill translates Relume/Framer references into
the equivalents that actually work and verify in this codebase.

## What It Does

- Reads Framer Motion reference code and maps each hook (`useScroll`, `useMotionValue`,
  `whileInView`, marquee classes) to its Clay DS native equivalent.
- **Mouse-move parallax** via CSS custom props `--mx/--my` + a `mousemove` listener (60fps, no
  React re-renders), with depth-scale guidance.
- **Scroll-driven parallax** via a JS scroll listener with **section-anchored** progress
  (`-rect.top / rect.height`), reproducing the reference's `useTransform` ranges exactly —
  and explains why NOT to use CSS `animation-timeline: scroll()` (silent failure here).
- **Seamless marquee loops** (`translateY(0 → -50%)`, `margin-bottom` not `gap` so the seam
  never jumps), self-contained clipping, staggered columns.
- Handles `prefers-reduced-motion` per technique, plus preview-verification recipes and a
  finishing checklist.

## When to Use

- The user shares a Relume/Framer Motion reference and asks to add its animation to a section.
- Requests for mouse parallax, scroll parallax, entrance motion, or "make the media move".
- **Not** for GSAP timelines, standalone looping banners (`motion`), or full-layout
  Figma matching (`frame-building`).

## Key Files

`SKILL.md` (entry) · `PROMPT.md` (reference-mapping table, mouse/scroll/marquee patterns with
code, critical pitfalls, verification, finishing checklist, in-codebase references)

## Installation

```bash
mkdir -p ~/.claude/skills
git clone --filter=blob:none --sparse https://github.com/DaPulse/marketing-design-ai-hub.git /tmp/mdai-hub-install 2>/dev/null || (cd /tmp/mdai-hub-install && git pull)
cd /tmp/mdai-hub-install
git sparse-checkout set skills/ds-section-animations
git checkout
cp -r skills/ds-section-animations ~/.claude/skills/
```

Use it by typing `/ds-section-animations`, or just describe what you want.

---

**Owner:** Elior Siegelwachs · **Last updated by:** Elior Siegelwachs · **Last updated:** 2026-07-14
