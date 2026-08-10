# 06a · Animation Building

**Role:** add the motion (GSAP / CSS / JS) to the stitched document, one frame at a time, per the
per-frame prompts and the general brief. Runs once per frame (and per fix iteration in Loop B).

**Inputs:** the stitched doc (05); per-frame prompt + general brief + the **before→after transition
delta** (02); motion baseline (`gsap` + `motion`). The delta is the source of truth for *what*
moves and in which direction/distance — animate the real change, not a guess. The brief takes
precedence over any inconsistent per-frame prompt.

**Method — route to the right engine skill for the motion type:**
- `motion` — reveal/collapse/emerge, loop shape (yoyo / continuous / forward-reset), seam-proof
  looping (period-snapping; prove value AND velocity at the boundary).
- `motion` — orchestrated multi-beat element entrances (box→text→rows).
- `motion` — cycling headline word (vertical roll + width morph).
- `motion` — endless horizontal scroll rows.
- `gsap` — timeline/easing/stagger primitives; `frame-building` for the fixed stage.

**Hard constraints:**
- **Element reuse, not duplication.** A logo/product/text block shared across frames is the **same
  continuous DOM node** carried through — never re-created per frame (duplicates cause
  flashing/popping/misaligned overlaps at transitions). Actively check, don't assume.
- **Restraint** — don't animate everything; be deliberate about density and pacing.
- Smooth easing per the motion baseline; expose timing as named constants for easy tuning.

**Fix mode (Loop B):** apply 06b's fix-prompt as a targeted edit, not a rebuild.

**Output / handoff:** the stitched doc with this frame's motion → stage 06b.
**Standalone:** yes — animate a specific frame/section.
