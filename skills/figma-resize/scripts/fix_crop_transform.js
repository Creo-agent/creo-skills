// fix_crop_transform.js — R8 post-pass
//
// imageTransform is not reliably preserved through a resize. Even with a correct uniform uScale,
// an image fill in CROP mode can end up with different X and Y scale factors in its transform
// matrix — the photo is squashed inside an otherwise correctly-sized frame.
//
// Run on every placement, after fix_mask_images.js (so the rect is already where it belongs).
//
// NEVER "fix" this by switching CROP to FILL. FILL re-centres automatically, which discards the
// designer's crop: a portrait framed on someone's face becomes a shot of their torso. The
// geometric-mean correction below removes the squash and keeps whatever was chosen to be visible.
//
// Validated 2026-07-16 on the Community Hub 1200×1200 LI frame, where three of five person
// bubbles carried X 0.993 against Y 1.089 and every other check passed.

const CONFIG = {
  frameId: "OUTPUT_FRAME_ID",
  tolerance: 0.01,     // 1% — below this, treat X and Y as uniform and leave the fill alone
};

const r4 = (n) => (typeof n === "number" && isFinite(n) ? Math.round(n * 10000) / 10000 : null);

const frame = await figma.getNodeByIdAsync(CONFIG.frameId);
if (!frame) throw new Error("Frame not found: " + CONFIG.frameId);

const targets = [];
(function collect(node) {
  if (Array.isArray(node.fills) && node.fills.some((f) => f.type === "IMAGE")) targets.push(node);
  (node.children || []).forEach(collect);
})(frame);

const report = [];

for (const node of targets) {
  let changed = false;

  const next = node.fills.map((fill) => {
    if (fill.type !== "IMAGE") return fill;

    // FILL fills are auto-centred by Figma and are always correct — leave them.
    if (fill.scaleMode !== "CROP") {
      report.push({ node: node.name, status: "skipped", reason: "scaleMode " + fill.scaleMode });
      return fill;
    }
    if (!fill.imageTransform) {
      report.push({ node: node.name, status: "skipped", reason: "no imageTransform" });
      return fill;
    }

    const T = fill.imageTransform;   // [[a, c, tx], [b, d, ty]]
    const sx = T[0][0];
    const sy = T[1][1];

    if (Math.abs(sx - sy) < CONFIG.tolerance) {
      report.push({ node: node.name, status: "already-uniform", x: r4(sx), y: r4(sy) });
      return fill;
    }

    const u = Math.sqrt(sx * sy);    // geometric mean — same principle as R2

    // preserve the crop centre in layer UV space, so the same part of the photo stays visible
    const centerX = T[0][2] + sx / 2;
    const centerY = T[1][2] + sy / 2;

    changed = true;
    report.push({
      node: node.name, status: "fixed",
      before: { x: r4(sx), y: r4(sy) },
      after:  { x: r4(u),  y: r4(u)  },
      squashPct: r4(Math.abs(sx - sy) / Math.min(sx, sy) * 100),
    });

    return {
      ...fill,
      imageTransform: [
        [u, 0, centerX - u / 2],
        [0, u, centerY - u / 2],
      ],
    };
  });

  if (changed) node.fills = next;
}

return {
  imageNodesFound: targets.length,
  fixed: report.filter((r) => r.status === "fixed").length,
  alreadyUniform: report.filter((r) => r.status === "already-uniform").length,
  skipped: report.filter((r) => r.status === "skipped").length,
  report,
};
