# 08 · Final Validation

**Role:** the last gate. Compare the finished, exported deliverable against the original Figma
storyboard and the stated intent, catching any drift accumulated anywhere in the pipeline.

**Inputs:** the exported output(s) from 07 (HTML/CSS, MP4, and/or GIF); the original Figma storyboard
(all source frames); the general brief + per-frame prompts + sequence class + loop-restart logic (02).

**Method (mirror stage 04's approach, applied to the whole animation):**
- **Structured / data-level** — pull Figma data via MCP / the Figma skill (consistent with 04) and
  check tokens, spacing, and positioning survived into the delivered artifact.
- **Visual** — vision-compare frames of the final animation against the original Figma frames and the
  brief's intent: composition, motion direction, timing, and overall fidelity (including any loss
  introduced by export). For a loop, confirm the restart is seamless in the delivered file.
- Score "what was supposed to be created" vs "what was created" (same spirit as the 04 rubric,
  at sequence level). Flag: missing elements, animations not matching intent, timing/composition
  drift, fidelity/export loss.

**Routing (don't restart the pipeline):** route a specific discrepancy back to the responsible stage
— composition/transition issue → 06c; static fidelity → 04 (→03); timing/easing → 06a; conversion
artifact → 07. Re-run only the affected stage(s).

**Output / handoff:** a validation report (intended vs actual, with flagged discrepancies). If clean,
**DELIVERED**. **Standalone:** yes — validate any finished animation against a Figma storyboard + intent.
