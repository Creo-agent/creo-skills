# 05 · Frame Stitching

**Role:** combine all QA-approved static frames into one HTML/CSS document, in sequence. Purely
mechanical — lays the foundation for animation. Nothing is animated, restyled, or re-QA'd here.

**Precondition:** **every** frame has passed stage 04 (≥95). Never stitch a partial/unapproved set.

**Do:** concatenate the approved frames in sequence order into a single document (e.g. stacked
sections / positioned layers per the sequence class from 02). Keep shared elements identifiable so
stage 06a can treat them as one continuous node (element reuse). Resist adding animation, styling
tweaks, or "cleanup" — that belongs to 06a and would invalidate the 04 approvals.

**Output / handoff:** one combined HTML/CSS document → Loop B (06a/06b), then 06c.
**QA:** none (deliberate — accuracy was gated at 04). **Standalone:** yes — assemble approved frames.
