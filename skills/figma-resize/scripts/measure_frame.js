// measure_frame.js — the measurement probe
//
// Runs inside Figma via use_figma. Walks a frame and emits the JSON contract defined in
// reference/PRE-RESIZE-MEASUREMENT.md. Run it on the MASTER before any clone exists, and on
// each OUTPUT frame at gate step 9b.
//
// Load the figma-use skill before calling use_figma. Set the three CONFIG values below.
//
// Node identity is the INDEX PATH ("0/2/1"), not the name. Figma names duplicate constantly;
// matching by name pairs the wrong nodes and produces a confidently wrong diff. See
// PRE-RESIZE-MEASUREMENT.md § Node matching.

const CONFIG = {
  nodeId:    "SOURCE_NODE_ID",   // frame to measure
  role:      "master",           // "master" | "output"
  placement: null,               // null on master; "STORY" | "FB" | "LI" on an output
};

// ---------- helpers ----------

const MIXED = figma.mixed;
const isMixed = (v) => v === MIXED;
const r2 = (n) => (typeof n === "number" && isFinite(n) ? Math.round(n * 100) / 100 : null);
const r4 = (n) => (typeof n === "number" && isFinite(n) ? Math.round(n * 10000) / 10000 : null);

function toHex(c) {
  if (!c) return null;
  const h = (v) => Math.round(Math.max(0, Math.min(1, v)) * 255).toString(16).padStart(2, "0");
  return "#" + h(c.r) + h(c.g) + h(c.b);
}

function paint(p) {
  if (!p) return null;
  const out = { type: p.type, opacity: r2(p.opacity != null ? p.opacity : 1) };
  if (p.visible === false) out.visible = false;

  if (p.type === "SOLID") {
    out.hex = toHex(p.color);
  } else if (p.type && p.type.startsWith("GRADIENT")) {
    // gradientTransform carries the angle — R18 checks this survives the resize
    out.gradientTransform = p.gradientTransform
      ? p.gradientTransform.map((row) => row.map(r4))
      : null;
    out.stops = (p.gradientStops || []).map((s) => ({
      position: r4(s.position),
      hex: toHex(s.color),
      a: r2(s.color && s.color.a != null ? s.color.a : 1),
    }));
  } else if (p.type === "IMAGE") {
    out.scaleMode = p.scaleMode;
    out.imageHash = p.imageHash || null;
    if (p.imageTransform) {
      const T = p.imageTransform;
      out.imageTransform = T.map((row) => row.map(r4));
      out.transformScaleX = r4(T[0][0]);   // R8 compares these two
      out.transformScaleY = r4(T[1][1]);
    }
    if (p.scalingFactor != null) out.scalingFactor = r4(p.scalingFactor);
    if (p.rotation != null) out.rotation = p.rotation;
  }
  return out;
}

function paints(v) {
  if (!v || isMixed(v) || !Array.isArray(v)) return isMixed(v) ? "MIXED" : [];
  return v.map(paint).filter(Boolean);
}

function effects(v) {
  if (!v || !Array.isArray(v)) return [];
  return v.map((e) => {
    const o = { type: e.type, visible: e.visible !== false };
    if (e.radius != null) o.radius = r2(e.radius);
    if (e.spread != null) o.spread = r2(e.spread);
    if (e.offset) o.offset = { x: r2(e.offset.x), y: r2(e.offset.y) };
    if (e.color) { o.hex = toHex(e.color); o.a = r2(e.color.a != null ? e.color.a : 1); }
    return o;
  });
}

function textProps(node) {
  const fn = node.fontName;
  const fs = node.fontSize;
  const ls = node.letterSpacing;
  const lh = node.lineHeight;
  return {
    characters: node.characters,                       // R12 diffs this verbatim
    fontFamily: isMixed(fn) ? "MIXED" : (fn ? fn.family : null),
    fontStyle:  isMixed(fn) ? "MIXED" : (fn ? fn.style  : null),
    fontSize:   isMixed(fs) ? "MIXED" : r2(fs),        // R22 excludes this; R12 permits reducing it
    letterSpacing: isMixed(ls) ? "MIXED" : (ls ? { unit: ls.unit, value: r2(ls.value) } : null),
    lineHeight:    isMixed(lh) ? "MIXED" : (lh ? { unit: lh.unit, value: r2(lh.value) } : null),
    textAutoResize: node.textAutoResize || null,
    textAlignHorizontal: node.textAlignHorizontal || null,
  };
}

// ---------- walk ----------

const nodes = [];
const maskGroups = [];
const aspectRatios = {};

function walk(node, path, depth) {
  const abs = node.absoluteBoundingBox || null;

  const rec = {
    path,
    id: node.id,
    name: node.name,
    type: node.type,
    depth,
    abs: abs ? { x: r2(abs.x), y: r2(abs.y), width: r2(abs.width), height: r2(abs.height) } : null,
    local: {
      x: r2(node.x), y: r2(node.y),
      width: r2(node.width), height: r2(node.height),
    },
    rotation: r2(node.rotation != null ? node.rotation : 0),
    opacity: r2(node.opacity != null ? node.opacity : 1),
    visible: node.visible !== false,
  };

  if (node.isMask) rec.isMask = true;
  if (node.cornerRadius != null) {
    rec.cornerRadius = isMixed(node.cornerRadius) ? "MIXED" : r2(node.cornerRadius);
  }

  const f = paints(node.fills);
  if (f === "MIXED") rec.fills = "MIXED";
  else if (f.length) rec.fills = f;

  const s = paints(node.strokes);
  if (s !== "MIXED" && s.length) rec.strokes = s;

  const e = effects(node.effects);
  if (e.length) rec.effects = e;

  if (node.type === "TEXT") rec.text = textProps(node);

  // first image fill, hoisted for convenience — R8's check reads this
  if (Array.isArray(rec.fills)) {
    const img = rec.fills.find((p) => p.type === "IMAGE");
    if (img) rec.image = img;
  }

  // aspect ratio, the R1/R2/R9 check
  if (rec.local.width && rec.local.height) {
    aspectRatios[path] = r4(rec.local.width / rec.local.height);
  }

  nodes.push(rec);

  const kids = node.children || [];

  // mask group detection: a container whose children include a mask (R5/R7)
  if (kids.length) {
    const maskIdx = kids.findIndex((c) => c.isMask);
    if (maskIdx !== -1) {
      const imgIdx = kids.findIndex(
        (c) => !c.isMask && Array.isArray(c.fills) && c.fills.some((p) => p.type === "IMAGE")
      );
      if (imgIdx !== -1) {
        const mAbs = kids[maskIdx].absoluteBoundingBox;
        const iAbs = kids[imgIdx].absoluteBoundingBox;
        maskGroups.push({
          path,
          maskPath: path + "/" + maskIdx,
          imagePath: path + "/" + imgIdx,
          absDelta: mAbs && iAbs
            ? { x: r2(mAbs.x - iAbs.x), y: r2(mAbs.y - iAbs.y) }
            : null,
        });
      }
    }
  }

  kids.forEach((child, i) => walk(child, path + "/" + i, depth + 1));
}

// ---------- role candidates ----------
// Suggestions only. RESIZE-WORKFLOW.md Step 3 / ASK-DONT-GUESS.md confirm roles with the user
// when ambiguous — the probe never decides which node "is" the logo, headline or CTA. These
// feed R32/R33/R38 (microcopy/CTA size floors, CTA-follows-master) the same way logoCandidates
// already feeds R11.

function candidates() {
  const logo = [], icon = [], cta = [], headline = [];
  const textNodes = nodes.filter((n) => n.type === "TEXT");
  const maxFontSize = Math.max(
    0, ...textNodes.map((n) => (typeof n.text?.fontSize === "number" ? n.text.fontSize : 0))
  );

  for (const n of nodes) {
    const name = (n.name || "").toLowerCase();
    if (name.includes("logo") || name.includes("brand") || name.includes("monday")) {
      logo.push(n.path);
    }
    const w = n.local.width, h = n.local.height;
    const smallSquare = w && h && w <= 64 && h <= 64 && Math.abs(w - h) <= 8;
    if (name.includes("icon") || smallSquare) icon.push(n.path);

    // CTA: name says so, or a frame/component wrapping a single text child with a solid fill
    // (the capsule-button shape) — checked on the container, not the label text itself.
    if (name.includes("cta") || name.includes("button") || name.includes("capsule")) {
      cta.push(n.path);
    }
  }

  // The CTA's own TEXT label: the text node whose nearest ancestor path is a CTA candidate.
  const ctaLabelPaths = textNodes
    .filter((n) => cta.some((c) => n.path.startsWith(c + "/")))
    .map((n) => n.path);

  // Headline: the TEXT node(s) at the largest font size, name hints aside — this is what
  // "dominant H1" (R34) means operationally when no name says "headline" explicitly.
  for (const n of textNodes) {
    const name = (n.name || "").toLowerCase();
    const isNamedHeadline = name.includes("headline") || name.includes("title") ||
      name.includes("heading") || /\bh1\b/.test(name);
    const isLargestText = maxFontSize > 0 && n.text?.fontSize === maxFontSize;
    if (isNamedHeadline || isLargestText) headline.push(n.path);
  }

  return {
    logoCandidates: logo,
    iconCandidates: icon,
    ctaCandidates: cta,
    ctaLabelCandidates: ctaLabelPaths,
    headlineCandidates: headline,
  };
}

// ---------- run ----------

const frame = await figma.getNodeByIdAsync(CONFIG.nodeId);
if (!frame) throw new Error("Node not found: " + CONFIG.nodeId + " (wrong id, or wrong page)");

walk(frame, "0", 0);

const fAbs = frame.absoluteBoundingBox;
const cand = candidates();

return {
  meta: {
    fileKey: figma.fileKey || null,
    nodeId: CONFIG.nodeId,
    frameName: frame.name,
    parentName: frame.parent ? frame.parent.name : null,   // R28's parenting half
    parentId: frame.parent ? frame.parent.id : null,
    role: CONFIG.role,
    placement: CONFIG.placement,
    frameAbs: fAbs
      ? { x: r2(fAbs.x), y: r2(fAbs.y), width: r2(fAbs.width), height: r2(fAbs.height) }
      : null,
    nodeCount: nodes.length,
  },
  nodes,
  derived: {
    maskGroups,                                  // present-but-empty means "no masks", not "probe failed"
    aspectRatios,
    textNodeCount: nodes.filter((n) => n.type === "TEXT").length,
    logoCandidates: cand.logoCandidates,
    iconCandidates: cand.iconCandidates,
    ctaCandidates: cand.ctaCandidates,
    ctaLabelCandidates: cand.ctaLabelCandidates,
    headlineCandidates: cand.headlineCandidates,
  },
};
