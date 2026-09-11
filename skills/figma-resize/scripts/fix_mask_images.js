// fix_mask_images.js — R5 / R7 post-pass
//
// group.resize() does not reliably keep an image rect aligned to the mask shape that clips it.
// After scaling, the image drifts — usually in Y — and the masked photo shows background.
// Run this on every placement, after the geometry pass, BEFORE fix_crop_transform.js.
//
// Strategy: shortcut → verify → converge.
//
//   1. Try the simple local-coordinate assignment. It is correct whenever the wrapper group
//      carries no residual scale transform, which is most of the time.
//   2. VERIFY in absolute space. Skipping this is how the bug ships: the shortcut succeeds
//      often enough to look reliable and fails silently when it doesn't.
//   3. If it failed, converge in absolute space by iterating.
//
// On the k-factor: local and canvas coordinates differ by the wrapper's scale s, so moving a
// node by ΔC canvas pixels means changing its local coordinate by ΔC / s. We derive k = 1/s as
// (local width / absolute width) rather than from a position ratio, because position ratios
// divide by a value that approaches zero for any node near the frame origin. Iterating also
// means the result does not depend on getting the direction of that factor right analytically —
// it converges either way.

const CONFIG = {
  frameId: "OUTPUT_FRAME_ID",
  tolerancePx: 5,      // R7's documented threshold for "aligned"
  maxIterations: 4,
};

const r2 = (n) => (typeof n === "number" && isFinite(n) ? Math.round(n * 100) / 100 : null);

const frame = await figma.getNodeByIdAsync(CONFIG.frameId);
if (!frame) throw new Error("Frame not found: " + CONFIG.frameId);

// --- collect every mask group in the frame ---
const groups = [];
(function collect(node) {
  const kids = node.children || [];
  if (kids.length) {
    const mask = kids.find((c) => c.isMask);
    const image = kids.find(
      (c) => !c.isMask && Array.isArray(c.fills) && c.fills.some((f) => f.type === "IMAGE")
    );
    if (mask && image) groups.push({ container: node, mask, image });
  }
  kids.forEach(collect);
})(frame);

const misalignment = (mask, image) => {
  const m = mask.absoluteBoundingBox;
  const i = image.absoluteBoundingBox;
  if (!m || !i) return null;
  return { dx: m.x - i.x, dy: m.y - i.y, worst: Math.max(Math.abs(m.x - i.x), Math.abs(m.y - i.y)) };
};

const report = [];

for (const { mask, image } of groups) {
  const before = misalignment(mask, image);
  if (!before) {
    report.push({ node: image.name, status: "skipped", reason: "no absoluteBoundingBox" });
    continue;
  }

  if (before.worst <= CONFIG.tolerancePx) {
    report.push({ node: image.name, status: "already-aligned", worstPx: r2(before.worst) });
    continue;
  }

  const origX = image.x, origY = image.y;

  // 1. shortcut
  image.x = mask.x;
  image.y = mask.y;
  image.resize(mask.width, mask.height);

  // 2. verify in absolute space
  let after = misalignment(mask, image);
  if (after && after.worst <= CONFIG.tolerancePx) {
    report.push({
      node: image.name, status: "fixed-shortcut",
      beforePx: r2(before.worst), afterPx: r2(after.worst),
    });
    continue;
  }

  // 3. converge — the wrapper has a residual scale transform
  image.x = origX;
  image.y = origY;
  image.resize(mask.width, mask.height);

  let iterations = 0;
  after = misalignment(mask, image);
  while (after && after.worst > CONFIG.tolerancePx && iterations < CONFIG.maxIterations) {
    const iAbs = image.absoluteBoundingBox;
    const kX = iAbs && iAbs.width  ? image.width  / iAbs.width  : 1;
    const kY = iAbs && iAbs.height ? image.height / iAbs.height : 1;

    image.x += after.dx * kX;
    image.y += after.dy * kY;

    iterations++;
    after = misalignment(mask, image);
  }

  report.push({
    node: image.name,
    status: after && after.worst <= CONFIG.tolerancePx ? "fixed-converged" : "UNRESOLVED",
    beforePx: r2(before.worst),
    afterPx: after ? r2(after.worst) : null,
    iterations,
  });
}

return {
  maskGroupsFound: groups.length,
  fixed: report.filter((r) => r.status.startsWith("fixed")).length,
  alreadyAligned: report.filter((r) => r.status === "already-aligned").length,
  unresolved: report.filter((r) => r.status === "UNRESOLVED").length,
  report,
};
