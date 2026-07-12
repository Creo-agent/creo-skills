#!/usr/bin/env python3
"""
Nano Banana resize helper — mirrors the Resizing Nano Banana Figma plugin's
Gemini calls so the skill can run outside Figma on plain image files.

Subcommands:
  analyze   Fallback master-design analysis via gemini-2.0-flash.
            ONLY use this if the model running the skill has no vision.
            (If Claude can see images, it should analyze the master itself.)

  generate  Generate one resized creative via gemini-3-pro-image-preview,
            using the same two-call (system -> ack -> user) pattern and
            imageConfig (image_size + optional aspectRatio) as the plugin.

API key resolution order: --api-key, then $GEMINI_API_KEY, then $GOOGLE_API_KEY.
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

IMAGE_MODEL = "gemini-3-pro-image-preview"
FLASH_MODEL = "gemini-2.0-flash"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

# Same supported ratios the plugin maps to.
SUPPORTED_RATIOS = {
    "1:1": 1 / 1, "2:3": 2 / 3, "3:2": 3 / 2, "3:4": 3 / 4, "4:3": 4 / 3,
    "4:5": 4 / 5, "5:4": 5 / 4, "9:16": 9 / 16, "16:9": 16 / 9, "21:9": 21 / 9,
}

EXTRACTION_PROMPT = """Analyze this ad design. Be concise (200 words max).

VISUAL: What images/photos/illustrations? Position? Container style (rounded, bordered)?
GRAPHIC: Background type? Decorative elements? Overall style?
TEXT: Exact headline, subheadline, CTA text.
LOGO: Description, position, count.
COLORS: Background, text, accent, CTA colors.
COMPOSITION: Layout structure, visual hierarchy, spacing.
STYLE: Mood, design trend.

Output a brief that helps recreate this design at different sizes."""


def resolve_key(cli_key):
    key = cli_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("No Gemini API key. Pass --api-key or set GEMINI_API_KEY / GOOGLE_API_KEY.")
    return key


def b64_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def aspect_ratio_if_needed(w, h):
    """Return an explicit aspectRatio only for extreme ratios (nearest diff > 1.0)."""
    target = w / h
    best, best_diff = None, float("inf")
    for ratio, val in SUPPORTED_RATIOS.items():
        d = abs(target - val)
        if d < best_diff:
            best, best_diff = ratio, d
    return best if best_diff > 1.0 else None


def post(url, payload, retries, delay_s, label=""):
    """POST JSON with exponential backoff; 503 gets a 1.5x multiplier (as in plugin)."""
    data = json.dumps(payload).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json"}, method="POST"
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")
            transient = e.code in (500, 503, 429) or "deadline" in body.lower()
            if transient and attempt < retries - 1:
                mult = 1.5 if e.code == 503 else 1.0
                wait = delay_s * (2 ** attempt) * mult
                print(f"  [{label}] {e.code}, retrying in {wait:.0f}s "
                      f"(attempt {attempt + 1}/{retries})", file=sys.stderr)
                time.sleep(wait)
                continue
            sys.exit(f"Gemini API error {e.code} [{label}]: {body}")
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                wait = delay_s * (2 ** attempt)
                print(f"  [{label}] network error, retrying in {wait:.0f}s", file=sys.stderr)
                time.sleep(wait)
                continue
            sys.exit(f"Network error [{label}]: {e}")
    sys.exit(f"Exhausted retries [{label}]")


def extract_image_b64(resp):
    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inline_data") or part.get("inlineData")
            if inline and inline.get("data"):
                return inline["data"]
    return None


def extract_text(resp):
    out = []
    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            if "text" in part:
                out.append(part["text"])
    return "
".join(out).strip()


def cmd_analyze(args):
    key = resolve_key(args.api_key)
    url = ENDPOINT.format(model=FLASH_MODEL, key=key)
    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"inline_data": {"mime_type": "image/png", "data": b64_file(args.master)}},
                {"text": EXTRACTION_PROMPT},
            ],
        }],
        "generationConfig": {"maxOutputTokens": 400},
    }
    resp = post(url, payload, retries=3, delay_s=3, label="analyze")
    brief = extract_text(resp)
    if not brief:
        sys.exit("No brief returned from gemini-2.0-flash.")
    print(brief)


def cmd_generate(args):
    key = resolve_key(args.api_key)
    url = ENDPOINT.format(model=IMAGE_MODEL, key=key)

    with open(args.system_prompt) as f:
        system_prompt = f.read()
    with open(args.user_prompt) as f:
        user_prompt = f.read()

    master_b64 = b64_file(args.master)

    # --- Call 1: system prompt + master image (prime the conversation) ---
    call1 = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": system_prompt},
                {"inline_data": {"mime_type": "image/png", "data": master_b64}},
            ],
        }],
    }
    resp1 = post(url, call1, retries=5, delay_s=5, label="system")

    # --- Call 2: replay context + model ack + user prompt (+ logo) ---
    user_parts = [{"text": user_prompt}]
    if args.logo:
        user_parts.append(
            {"inline_data": {"mime_type": "image/png", "data": b64_file(args.logo)}}
        )

    contents = [{
        "role": "user",
        "parts": [
            {"text": system_prompt},
            {"inline_data": {"mime_type": "image/png", "data": master_b64}},
        ],
    }]
    cands = resp1.get("candidates")
    if cands and cands[0].get("content"):
        contents.append({"role": "model", "parts": cands[0]["content"]["parts"]})
    contents.append({"role": "user", "parts": user_parts})

    image_config = {"image_size": args.resolution}
    ar = aspect_ratio_if_needed(args.width, args.height)
    if ar:
        image_config["aspectRatio"] = ar
        print(f"  [generate] extreme ratio {args.width}x{args.height} -> aspectRatio {ar}",
              file=sys.stderr)

    call2 = {"contents": contents, "generationConfig": {"imageConfig": image_config}}
    resp2 = post(url, call2, retries=3, delay_s=2, label="generate")

    img_b64 = extract_image_b64(resp2)
    if not img_b64:
        sys.exit(f"No image in response. Raw: {json.dumps(resp2)[:800]}")
    with open(args.out, "wb") as f:
        f.write(base64.b64decode(img_b64))
    print(f"Wrote {args.out} ({args.width}x{args.height}, {args.resolution})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--api-key", help="Gemini API key (else GEMINI_API_KEY / GOOGLE_API_KEY)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="Fallback master analysis via gemini-2.0-flash")
    a.add_argument("--master", required=True, help="path to master design image")
    a.set_defaults(func=cmd_analyze)

    g = sub.add_parser("generate", help="Generate one resized creative")
    g.add_argument("--master", required=True, help="path to master design PNG")
    g.add_argument("--logo", help="path to logo PNG (optional)")
    g.add_argument("--system-prompt", required=True, help="path to rendered system prompt .txt")
    g.add_argument("--user-prompt", required=True, help="path to rendered user prompt .txt")
    g.add_argument("--width", type=int, required=True)
    g.add_argument("--height", type=int, required=True)
    g.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    g.add_argument("--out", required=True, help="output PNG path")
    g.set_defaults(func=cmd_generate)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
